import plone.api as api
from graffiti.tile_listing.testing import GRAFFITI_TILE_LISTING_FUNCTIONAL_TESTING
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from zope.annotation.interfaces import IAnnotations


class TestTileListingView(InteraktivBasetilesTestCase):
    layer = GRAFFITI_TILE_LISTING_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        self.folder = api.content.create(
            container=self.portal, type='Folder', id='entry', title='Entry for authors'
        )
        self.entry_page = self.create_tilepage(_id='entry-page', container=self.folder, title='Entry page')
        api.content.create(container=self.folder, type='Document', id='doc-a', title='Document A')
        api.content.create(container=self.folder, type='Document', id='doc-b', title='Document B')
        api.content.create(container=self.portal, type='Document', id='doc-outside', title='Document outside')
        api.content.create(
            container=self.folder, type='Document', id='doc-hidden', title='Document hidden', exclude_from_nav=True
        )

        edit_rows = IAnnotations(self.entry_page)['edit']['tiles']
        tile_row = self.entry_page.create_tilerow(container=edit_rows)
        self.tile = self.entry_page.create_tile(
            container=tile_row, portaltype='TileListing', title='Listing'
        )

    def tearDown(self):
        self.delete(self.portal, self.folder)
        self.delete(self.portal, 'doc-outside')
        super().tearDown()

    def test_tile_uses_listing_view(self):
        self.assertEqual(self.tile['view_name'], 'view_tile_tilelisting')

    def test_view_mode_lists_folder_content(self):
        html = self.entry_page.render(self.tile)

        self.assertIn('tile-listing', html)
        self.assertIn('Document A', html)
        self.assertIn('Document B', html)

    def test_view_mode_excludes_entry_page_and_foreign_content(self):
        html = self.entry_page.render(self.tile)

        self.assertNotIn('Entry page', html)
        self.assertNotIn('Document outside', html)

    def test_view_mode_excludes_content_excluded_from_navigation(self):
        html = self.entry_page.render(self.tile)

        self.assertNotIn('Document hidden', html)

    def test_edit_mode_shows_placeholder_instead_of_listing(self):
        self.request.steps.append('@@edit')
        html = self.entry_page.render(self.tile)

        self.assertIn('tile-placeholder', html)
        self.assertIn('Entry for authors (2)', html)
        self.assertNotIn('Document A', html)
