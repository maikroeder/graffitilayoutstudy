import plone.api as api
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# noinspection PyUnresolvedReferences
from interaktiv import workingcopy
from plone.app.iterate.browser.info import BaselineInfoViewlet, CheckoutInfoViewlet
from plone.memoize.instance import memoize


class InteraktivInfoOriginalViewlet(BaselineInfoViewlet):
    index = ViewPageTemplateFile('templates/info_original.pt')

    def render(self):
        sm = getSecurityManager()
        working_copy = self.working_copy()
        if working_copy and (
                sm.checkPermission(ModifyPortalContent, self.context) or
                sm.checkPermission(ModifyPortalContent, working_copy)):
            return self.index()
        else:
            return str()

    def is_workingcopy(self):
        if self.context == self.working_copy():
            return True
        return False

    @memoize
    def working_copy(self):
        return workingcopy.get_working_copy(self.context)


class InteraktivInfoWorkingcopyViewlet(CheckoutInfoViewlet):
    index = ViewPageTemplateFile('templates/info_workingcopy.pt')

    def render(self):
        sm = getSecurityManager()
        original = self.original()
        if original and sm.checkPermission(ModifyPortalContent, self.context):
            return self.index()
        else:
            return ""

    def is_original(self):
        if self.context == self.original():
            return True
        return False

    @memoize
    def original(self):
        return workingcopy.get_original(self.context)

    def _getReference(self):
        return self.original()
