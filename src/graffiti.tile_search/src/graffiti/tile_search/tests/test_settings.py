from graffiti.tile_search.contract import SearchTileSettingsContract
from graffiti.tile_search.interfaces import ISearchTileSettings
from graffiti.tile_search.testing import GRAFFITI_TILE_SEARCH_FUNCTIONAL_TESTING
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getGlobalSiteManager, getMultiAdapter
from zope.interface import Interface, alsoProvides, implementer


class IProjectLayer(Interface):
    """ request layer of a project that uses its own search """


@implementer(ISearchTileSettings)
@adapter(ITilePage, IProjectLayer)
class ProjectSearchSettings:

    def __init__(self, context, request):
        pass

    def get_search_url(self):
        return 'http://nohost/plone/@@my-search'

    def get_livesearch_url(self):
        return None

    def get_parameters(self):
        return {'path': '/plone/documents'}

    def get_search_parameter_name(self):
        return 'q'


class TestSiteSearchSettings(SearchTileSettingsContract, InteraktivBasetilesTestCase):
    """ the default adapter fulfils the contract """
    layer = GRAFFITI_TILE_SEARCH_FUNCTIONAL_TESTING

    def get_settings(self):
        return getMultiAdapter((self.tilepage, self.request), ISearchTileSettings)


class TestProjectSearchSettings(SearchTileSettingsContract, InteraktivBasetilesTestCase):
    """ a project replaces the adapter for its own request layer """
    layer = GRAFFITI_TILE_SEARCH_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        getGlobalSiteManager().registerAdapter(ProjectSearchSettings)
        alsoProvides(self.request, IProjectLayer)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(ProjectSearchSettings)
        super().tearDown()

    def get_settings(self):
        return getMultiAdapter((self.tilepage, self.request), ISearchTileSettings)

    def test_tile_renders_search_of_the_project(self):
        edit_rows = IAnnotations(self.tilepage)['edit']['tiles']
        tile_row = self.tilepage.create_tilerow(container=edit_rows)
        tile = self.tilepage.create_tile(container=tile_row, portaltype='TileSearch', title='Search')

        html = self.tilepage.render(tile)

        self.assertIn('action="http://nohost/plone/@@my-search"', html)
        self.assertIn('<input type="hidden" name="path" value="/plone/documents"', html)
        self.assertNotIn('pat-livesearch', html)
        self.assertNotIn('data-pat-livesearch', html)
        self.assertIn('name="q"', html)
        self.assertNotIn('name="SearchableText"', html)
