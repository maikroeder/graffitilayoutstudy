from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api


class ExampleRecentView(BrowserView):
    """ Example of a frameless view (mode `view`): the ten most recently changed items.

    It renders only a fragment, no main template. That is the whole contract for mode `view`.
    """

    template = ViewPageTemplateFile('templates/example_recent.pt')

    def __call__(self) -> str:
        return self.template(self)

    def get_items(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = [
            brain for brain in catalog(sort_on='modified', sort_order='descending')
            if brain.portal_type != 'Plone Site'
        ][:10]
        return [
            {'title': brain.Title, 'url': brain.getURL(), 'modified': api.portal.get_localized_time(datetime=brain.modified, long_format=True)}
            for brain in brains
        ]
