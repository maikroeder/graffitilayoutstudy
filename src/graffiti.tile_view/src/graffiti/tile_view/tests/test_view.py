import json

import plone.api as api
from graffiti.tile_view.contract import EmbeddableViewsContract
from graffiti.tile_view.embed import EmbedError, extract_content, path_for_subrequest, render_view, with_ajax_load
from graffiti.tile_view.interfaces import IEmbeddableViewsProvider, MODE_AJAX_LOAD, MODE_VIEW
from graffiti.tile_view.testing import GRAFFITI_TILE_VIEW_FUNCTIONAL_TESTING
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getGlobalSiteManager, getMultiAdapter
from zope.interface import Interface, alsoProvides, implementer


class IProjectLayer(Interface):
    """ request layer of a project that registers its own views """


@implementer(IEmbeddableViewsProvider)
@adapter(ITilePage, IProjectLayer)
class ProjectViewsProvider:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_views(self):
        root = api.portal.get().absolute_url()
        return [
            {'id': 'recent', 'title': 'Recent', 'description': '', 'url': f'{root}/@@tile-view-example-recent', 'mode': MODE_VIEW},
            {'id': 'sitemap', 'title': 'Sitemap', 'description': '', 'url': f'{root}/sitemap', 'mode': MODE_AJAX_LOAD},
        ]


class TestEmbedHelpers(InteraktivBasetilesTestCase):
    layer = GRAFFITI_TILE_VIEW_FUNCTIONAL_TESTING

    def test_path_for_subrequest_strips_host_and_keeps_query(self):
        url = self.portal.absolute_url() + '/@@search?SearchableText=x&b_size=5'
        self.assertEqual(path_for_subrequest(url, self.request), '/plone/@@search?SearchableText=x&b_size=5')

    def test_with_ajax_load_adds_or_keeps_parameter(self):
        self.assertEqual(with_ajax_load('http://nohost/plone/@@search'), 'http://nohost/plone/@@search?ajax_load=1')
        self.assertEqual(with_ajax_load('http://nohost/plone/@@search?a=1'), 'http://nohost/plone/@@search?a=1&ajax_load=1')

    def test_extract_content_removes_ajax_load_from_links(self):
        html = '<div id="content-core"><a href="http://nohost/plone/@@search?ajax_load=1&amp;sort_on=Date">x</a><form action="@@search?ajax_load=1"></form></div>'
        self.assertEqual(extract_content(html), '<a href="http://nohost/plone/@@search?sort_on=Date">x</a><form action="@@search"></form>')

    def test_extract_content_prefers_content_core_and_drops_frame_ids(self):
        html = '<html><body><div id="content"><h1>Title</h1><div id="content-core"><p id="x">Hello</p><div id="main-container">y</div></div></div></body></html>'
        self.assertEqual(extract_content(html), '<p id="x">Hello</p><div>y</div>')


class TestTileView(EmbeddableViewsContract, InteraktivBasetilesTestCase):
    """ the default adapter fulfils the contract and the tile renders its views """
    layer = GRAFFITI_TILE_VIEW_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        api.content.create(container=self.portal, type='Document', id='doc-a', title='Document A')
        edit_rows = IAnnotations(self.tilepage)['edit']['tiles']
        self.tile_row = self.tilepage.create_tilerow(container=edit_rows)
        self.tile = self.tilepage.create_tile(container=self.tile_row, portaltype='TileView', title='View')

    def tearDown(self):
        self.delete(self.portal, 'doc-a')
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.tilepage, self.request), IEmbeddableViewsProvider)

    def test_tile_uses_view_view(self):
        self.assertEqual(self.tile['view_name'], 'view_tile_tileview')

    def test_tile_without_view_is_hidden_for_visitors(self):
        html = self.tilepage.render(self.tile)
        self.assertNotIn('tile-view-embedded', html)

    def test_edit_mode_without_view_asks_to_choose(self):
        self.request.steps.append('@@edit')
        html = self.tilepage.render(self.tile)
        self.assertIn('tile-placeholder', html)
        self.assertIn('No view chosen yet', html)

    def test_frameless_view_is_embedded_as_fragment(self):
        self.tile['view_id'] = 'example-recent'
        html = self.tilepage.render(self.tile)

        self.assertIn('data-view-mode="view"', html)
        self.assertIn('tile-view-example-recent', html)
        self.assertIn('Document A', html)
        self.assertEqual(html.count('<html'), 1)  # only the wrapper of the tile itself

    def test_page_is_embedded_via_ajax_load_without_frame(self):
        self.tile['view_id'] = 'plone-search'
        html = self.tilepage.render(self.tile)

        self.assertIn('data-view-mode="ajax_load"', html)
        self.assertIn('name="SearchableText"', html)
        self.assertNotIn('id="portal-globalnav"', html)
        self.assertNotIn('id="portal-footer', html)
        self.assertNotIn('id="content"', html)
        self.assertEqual(html.count('<html'), 1)  # only the wrapper of the tile itself
        self.assertNotIn('ajax_load=', html)  # links inside lead to the normal page

    def test_unknown_view_id_renders_nothing_for_visitors(self):
        self.tile['view_id'] = 'does-not-exist'
        html = self.tilepage.render(self.tile)
        self.assertNotIn('tile-view-embedded', html)

        self.request.steps.append('@@edit')
        html = self.tilepage.render(self.tile)
        self.assertIn('no longer registered', html)

    def test_render_view_raises_for_unknown_id(self):
        with self.assertRaises(EmbedError):
            render_view(self.tilepage, self.request, 'does-not-exist')

    def test_edit_mode_shows_chosen_view(self):
        self.tile['view_id'] = 'plone-search'
        self.request.steps.append('@@edit')
        html = self.tilepage.render(self.tile)

        self.assertIn('Search page of Plone', html)
        self.assertIn('interim solution', html)
        self.assertNotIn('name="SearchableText"', html)

    def test_modal_lists_registered_views_with_selection(self):
        self.tile['view_id'] = 'plone-search'
        self.request.form['id'] = self.tile['id']
        modal = api.content.get_view(name='configure_tileview_modal', context=self.tilepage, request=self.request)
        html = modal()

        self.assertIn('<option value="example-recent"', html)
        self.assertIn('selected="selected">Search page of Plone', html)

    def test_update_content_stores_the_chosen_view(self):
        self.request.form['id'] = self.tile['id']
        self.request.form['view_id'] = 'example-recent'
        api.content.get_view(name='update_content', context=self.tilepage, request=self.request)()

        stored = self.tilepage.get_annotation_data_by_id(self.tile['id'], True)
        self.assertEqual(stored['view_id'], 'example-recent')


class TestProjectViewsProvider(EmbeddableViewsContract, InteraktivBasetilesTestCase):
    """ a project replaces the adapter for its own request layer """
    layer = GRAFFITI_TILE_VIEW_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        getGlobalSiteManager().registerAdapter(ProjectViewsProvider)
        alsoProvides(self.request, IProjectLayer)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(ProjectViewsProvider)
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.tilepage, self.request), IEmbeddableViewsProvider)

    def test_tile_offers_only_the_views_of_the_project(self):
        ids = [entry['id'] for entry in self.get_provider().get_views()]
        self.assertEqual(ids, ['recent', 'sitemap'])
