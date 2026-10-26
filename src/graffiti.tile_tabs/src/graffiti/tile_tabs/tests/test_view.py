import plone.api as api
from graffiti.tile_tabs.interfaces import ITabListsProvider
from graffiti.tile_tabs.testing import GRAFFITI_TILE_TABS_FUNCTIONAL_TESTING
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getGlobalSiteManager
from zope.interface import Interface, alsoProvides, implementer


class IEmptyLayer(Interface):
    """ request layer with a provider that delivers no tabs """


@implementer(ITabListsProvider)
@adapter(ITilePage, IEmptyLayer)
class EmptyTabsProvider:

    def __init__(self, context, request):
        pass

    def get_tabs(self):
        return []


class TestTileTabsView(InteraktivBasetilesTestCase):
    layer = GRAFFITI_TILE_TABS_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        self.folder = api.content.create(container=self.portal, type='Folder', id='entry', title='Entry for authors')
        self.entry_page = self.create_tilepage(_id='entry-page', container=self.folder, title='Entry page')
        api.content.create(container=self.folder, type='Document', id='doc-a', title='Document A')

        edit_rows = IAnnotations(self.entry_page)['edit']['tiles']
        tile_row = self.entry_page.create_tilerow(container=edit_rows)
        self.tile = self.entry_page.create_tile(container=tile_row, portaltype='TileTabs', title='Lists')

    def tearDown(self):
        self.delete(self.portal, self.folder)
        super().tearDown()

    def test_tile_uses_tabs_view(self):
        self.assertEqual(self.tile['view_name'], 'view_tile_tiletabs')

    def test_view_mode_renders_tabs_and_shows_the_first_panel(self):
        html = self.entry_page.render(self.tile)
        uid = self.tile['id']

        self.assertIn('tile-tabs', html)
        self.assertIn('role="tablist"', html)
        self.assertIn(f'data-tab="recent" aria-controls="tile-tabs-{uid}-recent" aria-selected="true"', html)
        self.assertIn(f'data-tab="mine" aria-controls="tile-tabs-{uid}-mine" aria-selected="false"', html)
        self.assertNotIn(f'id="tile-tabs-{uid}-recent" aria-labelledby="tile-tabs-{uid}-recent-tab" hidden', html)
        self.assertIn(f'id="tile-tabs-{uid}-mine" aria-labelledby="tile-tabs-{uid}-mine-tab" hidden="hidden"', html)
        self.assertIn('Document A', html)
        self.assertIn(f'href="{self.folder["doc-a"].absolute_url()}"', html)

    def test_view_mode_needs_no_jsinit(self):
        html = self.entry_page.render(self.tile)

        self.assertIn('data-jsinit=""', html)

    def test_edit_mode_shows_placeholder_with_tab_titles_and_counts(self):
        self.request.steps.append('@@edit')
        html = self.entry_page.render(self.tile)

        self.assertIn('tile-placeholder', html)
        self.assertIn('In this folder (1)', html)
        self.assertNotIn('role="tablist"', html)

    def test_tile_without_tabs_is_hidden_for_visitors(self):
        getGlobalSiteManager().registerAdapter(EmptyTabsProvider)
        try:
            alsoProvides(self.request, IEmptyLayer)
            html = self.entry_page.render(self.tile)
        finally:
            getGlobalSiteManager().unregisterAdapter(EmptyTabsProvider)

        self.assertNotIn('tile-tabs-nav', html)
