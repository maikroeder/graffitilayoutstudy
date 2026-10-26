# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser import BrowserView
# noinspection PyUnresolvedReferences
from interaktiv import workingcopy
from interaktiv.workingcopy.behaviors.workingcopy import IWorkingcopyBehavior
from plone.memoize.view import memoize


class ControlView(BrowserView):
    """ Information about workingcopy can operate """

    def checkin_allowed(self):
        """ Check if a checkin is allowed """
        if not IWorkingcopyBehavior.providedBy(self.context):
            return False

        if workingcopy.get_original(self.context) is None:
            return False

        check_permission = getSecurityManager().checkPermission
        if not check_permission(ModifyPortalContent, self.context):
            return False

        return True

    def checkout_allowed(self):
        """ Check if a checkout is allowed. """
        if not IWorkingcopyBehavior.providedBy(self.context):
            return False

        if workingcopy.get_working_copy(self.context) is not None:
            return False

        # check if its is a checkout
        if workingcopy.get_original(self.context) is not None:
            return False

        return True

    @memoize
    def cancel_allowed(self):
        """ Check to see if the user can cancel the checkout on the
            given working copy """
        if not IWorkingcopyBehavior.providedBy(self.context):
            return False

        if not workingcopy.get_original(self.context) and \
                not workingcopy.get_working_copy(self.context):
            return False

        return True
