from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api

# what is not counted as a document: the structure of the site
NOT_DOCUMENTS = ('Collection', 'TilePage')


class DocumentsCountView(BrowserView):
    """ Frameless view (mode `view` of the view tile): how many documents the current user may see.

    It renders only a fragment, no main template. Collections and tiles pages are not documents.
    The number follows the permissions of the current user, like the boxes of the dashboard.
    """

    template = ViewPageTemplateFile('templates/documents_count.pt')

    def __call__(self) -> str:
        return self.template(self)

    def count(self) -> int:
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type={'not': list(NOT_DOCUMENTS)})
        return len(brains)
