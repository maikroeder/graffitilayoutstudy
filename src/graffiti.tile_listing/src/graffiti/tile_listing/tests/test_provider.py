import plone.api as api
from graffiti.tile_listing.contract import ListingItemsProviderContract
from graffiti.tile_listing.interfaces import IListingItemsProvider
from graffiti.tile_listing.testing import GRAFFITI_TILE_LISTING_FUNCTIONAL_TESTING
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getGlobalSiteManager, getMultiAdapter
from zope.interface import Interface, alsoProvides, implementer


class IProjectLayer(Interface):
    """ request layer of a project that delivers its own entries """


@implementer(IListingItemsProvider)
@adapter(ITilePage, IProjectLayer)
class ProjectItemsProvider:

    def __init__(self, context, request):
        pass

    def get_label(self):
        return 'My documents'

    def get_items(self):
        return [{'title': 'From project', 'description': '', 'url': 'http://nohost/x', 'portal_type': 'Custom Type'}]


class TestFolderItemsProvider(ListingItemsProviderContract, InteraktivBasetilesTestCase):
    """ the default adapter fulfils the contract """
    layer = GRAFFITI_TILE_LISTING_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        self.folder = api.content.create(container=self.portal, type='Folder', id='entry', title='Entry')
        self.entry_page = self.create_tilepage(_id='entry-page', container=self.folder, title='Entry page')
        api.content.create(container=self.folder, type='Document', id='doc-a', title='Document A')

    def tearDown(self):
        self.delete(self.portal, self.folder)
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.entry_page, self.request), IListingItemsProvider)

    def test_default_lists_folder_content(self):
        provider = self.get_provider()

        self.assertEqual(provider.get_label(), 'Entry')
        self.assertEqual([item['title'] for item in provider.get_items()], ['Document A'])


class TestProjectItemsProvider(ListingItemsProviderContract, InteraktivBasetilesTestCase):
    """ a project replaces the adapter for its own request layer """
    layer = GRAFFITI_TILE_LISTING_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        getGlobalSiteManager().registerAdapter(ProjectItemsProvider)
        alsoProvides(self.request, IProjectLayer)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(ProjectItemsProvider)
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.tilepage, self.request), IListingItemsProvider)

    def test_tile_renders_entries_of_the_project(self):
        edit_rows = IAnnotations(self.tilepage)['edit']['tiles']
        tile_row = self.tilepage.create_tilerow(container=edit_rows)
        tile = self.tilepage.create_tile(container=tile_row, portaltype='TileListing', title='Listing')

        html = self.tilepage.render(tile)

        self.assertIn('From project', html)
        self.assertIn('contenttype-custom-type', html)
