from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
# noinspection PyUnresolvedReferences
from interaktiv import workingcopy as workingcopy_functions
from interaktiv.workingcopy.events.after_cancel import AfterCancelEvent
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from zope.component import getMultiAdapter
from zope.event import notify


class CancelView(BrowserView):
    template = ViewPageTemplateFile('templates/cancel.pt')

    def __call__(self):
        if 'form.button.Cancel' in self.request.form:
            self._check_permission()
            original = self._cancel(workingcopy=self.context)
            if 'no_redirect' in self.request.form:
                return original
            self._redirect(original)
        elif 'form.button.Keep' in self.request.form:
            self._redirect(self.context)
        else:
            return self.template(self)

    def _check_permission(self):
        control = getMultiAdapter(
            (self.context, self.request), name=u"workingcopy_control"
        )
        if not control.cancel_allowed():
            raise Exception(u"Not a checkout")
        return True

    def _cancel(self, workingcopy):
        original = workingcopy_functions.get_original(workingcopy)

        # delete the working copy an the relation entry
        setattr(original, ITERATE_RELATION_NAME, None)
        workingcopy_container = aq_parent(aq_inner(workingcopy))
        workingcopy_container.manage_delObjects([workingcopy.getId()])

        # set status message
        IStatusMessage(self.request).addStatusMessage(
            u'Arbeitskopie wurde verworfen!'
        )

        # fire event
        notify(AfterCancelEvent(original))

        return original

    def _redirect(self, obj):
        view_url = obj.restrictedTraverse(
            "@@plone_context_state").view_url()
        self.request.response.redirect(view_url)
