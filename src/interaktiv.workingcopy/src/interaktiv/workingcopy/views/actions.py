# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.content.browser.actions import DeleteConfirmationForm
from plone.app.content.browser.actions import ObjectDeleteView
from z3c.form import button


def is_unlocked(delete_form):
    return not delete_form.is_locked


class InteraktivDeleteConfirmationForm(DeleteConfirmationForm):
    """ We need to override this form to handle deletion of objects that are
    locked (e.g. it has an working copy).

    If an object is locked, we hide the button in delete confirmation form and
    also redirect, if the delete handler get calls directly.

    Caveat: We need to reimplement all the actions while overriding, because
    of the button.buttonAndHandler implementation.
    """

    @property
    def title(self):
        return safe_unicode(self.context.Title())

    def do_redirect(self, url, message=None, message_type='info',
                    raise_exception=None):
        if message is not None:
            # noinspection PyArgumentList
            IStatusMessage(self.request).add(message, type=message_type)

        if raise_exception is None:
            return self.request.response.redirect(url)
        raise raise_exception

    @button.buttonAndHandler(_(u'Delete'), name='Delete', condition=is_unlocked)
    def handle_delete(self, action):
        if self.is_locked:
            msg = _(u'${title} is locked and cannot be deleted.',
                    mapping={'title': self.title})
            return self.do_redirect(self.view_url(), msg)

        base_handler = super(InteraktivDeleteConfirmationForm,
                             self).handle_delete
        return base_handler(self, action)

    @button.buttonAndHandler(
        _(u'label_cancel', default=u'Cancel'), name='Cancel')
    def handle_cancel(self, action):
        base_handler = super(InteraktivDeleteConfirmationForm,
                             self).handle_cancel
        return base_handler(self, action)


class InteraktivObjectDeleteView(ObjectDeleteView):

    def do_action(self):
        form = InteraktivDeleteConfirmationForm(self.context, self.request)
        form.update()

        form_button = form.buttons['Delete']
        # delete by clicking the form button in delete_confirmation
        form.handlers.getHandler(button)(form, form_button)
