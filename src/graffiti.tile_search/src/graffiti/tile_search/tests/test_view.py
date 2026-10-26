from graffiti.tile_search.testing import GRAFFITI_TILE_SEARCH_FUNCTIONAL_TESTING
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from zope.annotation.interfaces import IAnnotations


class TestTileSearchView(InteraktivBasetilesTestCase):
    layer = GRAFFITI_TILE_SEARCH_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        edit_rows = IAnnotations(self.tilepage)['edit']['tiles']
        tile_row = self.tilepage.create_tilerow(container=edit_rows)
        self.tile = self.tilepage.create_tile(container=tile_row, portaltype='TileSearch', title='Search')
        self.second_tile = self.tilepage.create_tile(container=tile_row, portaltype='TileSearch', title='Search 2')

    def test_tile_uses_search_view(self):
        self.assertEqual(self.tile['view_name'], 'view_tile_tilesearch')

    def test_view_mode_renders_search_form_with_livesearch(self):
        html = self.tilepage.render(self.tile)
        portal_url = self.portal.absolute_url()

        self.assertIn('pat-livesearch', html)
        self.assertIn(f'action="{portal_url}/@@search"', html)
        self.assertIn(f'data-pat-livesearch="ajaxUrl:{portal_url}/@@ajax-search"', html)
        self.assertIn('name="SearchableText"', html)

    def test_input_id_is_unique_per_tile(self):
        html = self.tilepage.render(self.tile)
        second_html = self.tilepage.render(self.second_tile)

        self.assertIn(f'id="tile-search-{self.tile["id"]}"', html)
        self.assertIn(f'id="tile-search-{self.second_tile["id"]}"', second_html)
        self.assertNotEqual(self.tile['id'], self.second_tile['id'])

    def test_edit_mode_shows_placeholder_without_form(self):
        self.request.steps.append('@@edit')
        html = self.tilepage.render(self.tile)

        self.assertIn('tile-placeholder', html)
        self.assertNotIn('<form', html)
        self.assertNotIn('pat-livesearch', html)
