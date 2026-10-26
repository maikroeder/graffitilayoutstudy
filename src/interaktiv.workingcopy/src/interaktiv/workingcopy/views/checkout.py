# -*- coding: utf-8 -*-
import interaktiv.framework as framework
import plone.api as api
import transaction
from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from interaktiv.workingcopy.events.after_checkout import AfterCheckoutEvent
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.app.iterate.interfaces import IObjectCopier
from plone.locking.interfaces import STEALABLE_LOCK
# noinspection PyUnresolvedReferences
from zope import component
from zope.component import getMultiAdapter
from zope.event import notify


class CheckoutView(BrowserView):
    template = ViewPageTemplateFile('templates/checkout.pt')
    errors = []

    def __call__(self):
        self.errors = []
        if 'form.button.Checkout' in self.request.form:
            self._check_permission()
            self._validate()
            if not self.errors:
                working_copy = framework.sudo.execute_as_manager(
                    api.portal.get(),
                    self._checkout,
                    original=self.context,
                    container=aq_parent(self.context),
                    version_notice=self.request.form.get('version_notice', '')
                )
                # set status message
                IStatusMessage(self.request).addStatusMessage(
                    u'Arbeitskopie wurde erstellt!'
                )
                transaction.commit()
                if 'no_redirect' in self.request.form:
                    return True
                else:
                    self._redirect(working_copy)
            else:
                IStatusMessage(self.request).addStatusMessage(
                    u'\n'.join(self.errors),
                    'error'
                )
                return self.template(self)

        elif 'form.button.Cancel' in self.request.form:
            self._redirect(self.context)
        return self.template(self)

    def _check_permission(self):
        control = getMultiAdapter(
            (self.context, self.request), name=u"workingcopy_control"
        )
        if not control.checkout_allowed():
            raise Exception(
                u"[Fehler] Es ist nicht möglich eine "
                u"Arbeitskopie anzulegen. Entweder ist das Dokument noch "
                u"im Entwurf, es besteht bereits eine Arbeitskopie "
                u"oder es fehlt Ihnen die Berechtigung eine "
                u"Arbeitskopie anzulegen.")
        return True

    def _validate(self):
        if 'version_notice' in self.request.form.keys():
            if not self.request.form['version_notice']:
                self.errors.append(
                    u'Änderungsnotiz ist ein Pflichtfeld'
                )

    def _checkout(self, original, container, version_notice):
        # copy original recursively and set relation
        copier = component.queryAdapter(original, IObjectCopier)
        working_copy, relation = copier.copyTo(container)
        setattr(original, ITERATE_RELATION_NAME, relation)
        original.reindexObject('review_state')
        framework.locking.lock(context=original, lock_type=STEALABLE_LOCK)

        # set version notice
        working_copy.working_copy_version_notice = version_notice

        # set local_roles
        local_role_map = {}
        for entry in original.get_local_roles():
            if entry[0] in local_role_map:
                local_role_map[entry[0]].extend(list(entry[1]))
            else:
                local_role_map[entry[0]] = list(entry[1])
        for user_id in local_role_map:
            working_copy.manage_setLocalRoles(user_id, local_role_map[user_id])

        # fire event
        notify(AfterCheckoutEvent(original, working_copy, relation))

        return working_copy

    def _redirect(self, obj):
        view_url = obj.restrictedTraverse(
            "@@plone_context_state"
        ).view_url()
        self.request.response.redirect(view_url)
