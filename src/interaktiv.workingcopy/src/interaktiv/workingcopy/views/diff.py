from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# noinspection PyUnresolvedReferences
from interaktiv import workingcopy


class DiffView(BrowserView):
    template = ViewPageTemplateFile('templates/diff.pt')
    original = None
    working_copy = None

    def __call__(self):
        self.original = workingcopy.get_original(self.context)
        self.working_copy = workingcopy.get_working_copy(self.context)
        if not self.context == self.original and \
                not self.context == self.working_copy:
            raise AttributeError("Invalid Context")
        return self.template(self)

    def diffs(self):
        diff = getToolByName(self.context, 'portal_diff')
        changes = diff.createChangeSet(
            self.original,
            self.working_copy,
            id1="Original",
            id2="Arbeitskopie"
        )
        return changes
