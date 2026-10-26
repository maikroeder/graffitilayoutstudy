# -*- coding: utf-8 -*-
import interaktiv.framework as framework
from Acquisition import aq_base
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from interaktiv.workingcopy.events.after_checkin import AfterCheckinEvent
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.app.iterate.interfaces import IObjectCopier
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.locking.interfaces import STEALABLE_LOCK
from zc.relation.interfaces import ICatalog
# noinspection PyUnresolvedReferences
from zope import component
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds


class CheckinView(BrowserView):
    index = ViewPageTemplateFile('templates/checkin.pt')
    original_workflow_id = ''
    workingcopy_workflow_name = ''

    def __call__(self):
        if 'form.button.Checkin' in self.request.form:
            self._check_permission()
            merged_original = self._checkin(workingcopy=self.context)
            if 'no_redirect' in self.request.form:
                return True
            else:
                self._redirect(merged_original)
        elif 'form.button.Cancel' in self.request.form:
            self._redirect(self.context)
        else:
            return self.index(self)

    def _check_permission(self):
        control = getMultiAdapter(
            (self.context, self.request), name=u"workingcopy_control")
        if not control.checkin_allowed():
            raise Exception(u"Not a checkin")
        return True

    def _checkin(self, workingcopy):
        # get original and unlock it
        intids = getUtility(IIntIds)
        catalog = getUtility(ICatalog)
        relations = list(catalog.findRelations({
            'to_id': intids.queryId(aq_base(workingcopy)),
            'from_attribute': ITERATE_RELATION_NAME
        }))
        if relations:
            original = intids.getObject(relations[0].from_id)
            framework.locking.force_unlock(context=original, lock_type=STEALABLE_LOCK)

        # get workingcopy history before merge
        content_history_viewlet = ContentHistoryViewlet(
            workingcopy, self.request, None, None
        )
        content_history_viewlet.navigation_root_url = 'http://www.foo.com'
        content_history_viewlet.site_url = 'http://www.foo.com'
        workingcopy_history = content_history_viewlet.fullHistory()

        # merge workingcopy with original
        copier = component.queryAdapter(workingcopy, IObjectCopier)
        merged_original = copier.merge()

        # add checkin history message
        self._merge_history(
            to_object=merged_original,
            history=workingcopy_history
        )

        # set status message
        IStatusMessage(self.request).addStatusMessage(
            u'Arbeitskopie wurde mit dem Original ausgetauscht!'
        )

        # fire event
        notify(AfterCheckinEvent(merged_original))

        return merged_original

    def _merge_history(self, to_object, history):
        comments = self.request.form.get('comments', '')
        if comments:
            if len(history) > 1:
                history[-2]['comments'] = history[-2]['comments'] + comments
        history[-1]['comments'] = 'Arbeitskopie erstellt: %s' % getattr(
            self.context,
            'working_copy_version_notice',
            ''
        )

        # add checkin history message
        framework.history.add_history_message(
            obj=to_object,
            message={'type': 'workingcopy', 'data': history}
        )

        if self.workingcopy_workflow_name:
            wfh = list(to_object.workflow_history[self.original_workflow_id])
            wfh[-1]['history'] = history
            to_object.workflow_history[self.original_workflow_id] = tuple(wfh)

        return True

    def _redirect(self, obj):
        view_url = obj.restrictedTraverse(
            "@@plone_context_state").view_url()
        self.request.response.redirect(view_url)
