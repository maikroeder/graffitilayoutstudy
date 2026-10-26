import json

import plone.api as api
from graffiti.tile_dashboard.contract import DashboardBoxesProviderContract
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from graffiti.tile_dashboard.testing import GRAFFITI_TILE_DASHBOARD_FUNCTIONAL_TESTING
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from plone.app.testing import logout
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getGlobalSiteManager, getMultiAdapter
from zope.interface import Interface, alsoProvides, implementer


class IProjectLayer(Interface):
    """ request layer of a project that delivers its own boxes """


@implementer(IDashboardBoxesProvider)
@adapter(ITilePage, IProjectLayer)
class ProjectBoxesProvider:

    def __init__(self, context, request):
        pass

    def get_boxes(self):
        return [{'id': 'todo', 'title': 'My tasks', 'description': '', 'url': 'http://nohost/todo', 'urgent': True}]

    def get_counts(self):
        return {'todo': 42}


class TestTileDashboard(DashboardBoxesProviderContract, InteraktivBasetilesTestCase):
    """ the contract tests check the default adapter (one box per collection) """
    layer = GRAFFITI_TILE_DASHBOARD_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        # the test site has no default workflow, the numbers are tested with private and published content
        self.portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        self.folder = api.content.create(container=self.portal, type='Folder', id='entry', title='Entry')
        self.entry_page = self.create_tilepage(_id='entry-page', container=self.folder, title='Entry page')
        api.content.create(container=self.folder, type='Document', id='doc-private', title='Private document')
        published = api.content.create(container=self.folder, type='Document', id='doc-published', title='Published')
        api.content.transition(obj=published, transition='publish')
        path = '/'.join(self.folder.getPhysicalPath())
        self.collection = api.content.create(
            container=self.folder, type='Collection', id='all-documents', title='All documents',
            query=[
                {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.any', 'v': ['Document']},
                {'i': 'path', 'o': 'plone.app.querystring.operation.string.absolutePath', 'v': path},
            ]
        )
        api.content.transition(obj=self.folder, transition='publish')
        api.content.transition(obj=self.collection, transition='publish')

        edit_rows = IAnnotations(self.entry_page)['edit']['tiles']
        tile_row = self.entry_page.create_tilerow(container=edit_rows)
        self.tile = self.entry_page.create_tile(container=tile_row, portaltype='TileDashboard', title='Dashboard')

    def tearDown(self):
        self.login_as_manager()
        self.delete(self.portal, self.folder)
        super().tearDown()

    def login_as_manager(self):
        from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def get_provider(self):
        return getMultiAdapter((self.entry_page, self.request), IDashboardBoxesProvider)

    def get_counts(self):
        view = api.content.get_view(name='tile_dashboard_data', context=self.entry_page, request=self.request)
        return json.loads(view())['counts']

    def test_tile_uses_dashboard_view(self):
        self.assertEqual(self.tile['view_name'], 'view_tile_tiledashboard')

    def test_view_mode_renders_boxes_without_numbers(self):
        html = self.entry_page.render(self.tile)

        self.assertIn('data-jsinit="initGraffitiTileDashboard"', html)
        self.assertIn(f'data-url="{self.entry_page.absolute_url()}/@@tile_dashboard_data"', html)
        self.assertIn('data-box-id="all-documents"', html)
        self.assertIn('All documents', html)
        self.assertIn(f'href="{self.collection.absolute_url()}"', html)

    def test_default_marks_collections_tagged_todo_as_urgent(self):
        self.assertEqual([box['urgent'] for box in self.get_provider().get_boxes()], [False])
        api.content.create(
            container=self.folder, type='Collection', id='tasks', title='Tasks', subject=('todo',),
            query=[{'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.any', 'v': ['pending']}],
        )

        boxes = {box['id']: box['urgent'] for box in self.get_provider().get_boxes()}
        html = self.entry_page.render(self.tile)

        self.assertEqual(boxes, {'all-documents': False, 'tasks': True})
        self.assertEqual(html.count('data-urgent="true"'), 1)
        self.assertEqual(html.count('data-urgent="false"'), 1)
        self.assertEqual(html.count('tile-dashboard-todo"'), 1)  # the marker is only rendered for urgent boxes

    def test_counts_depend_on_the_current_user(self):
        self.assertEqual(self.get_counts(), {'all-documents': 2})

        logout()
        self.assertEqual(self.get_counts(), {'all-documents': 1})

    def test_data_view_is_not_cached(self):
        self.get_counts()
        self.assertEqual(self.request.response.getHeader('Cache-Control'), 'private, no-store')

    def test_edit_mode_shows_placeholder_with_box_titles(self):
        self.request.steps.append('@@edit')
        html = self.entry_page.render(self.tile)

        self.assertIn('tile-placeholder', html)
        self.assertIn('All documents', html)
        self.assertNotIn('tile-dashboard-count', html)

    def test_tile_without_boxes_is_hidden_for_visitors(self):
        self.delete(self.folder, self.collection)
        html = self.entry_page.render(self.tile)

        self.assertNotIn('tile-dashboard-boxes', html)

    def test_project_can_deliver_its_own_boxes(self):
        site_manager = getGlobalSiteManager()
        site_manager.registerAdapter(ProjectBoxesProvider)
        try:
            alsoProvides(self.request, IProjectLayer)
            html = self.entry_page.render(self.tile)

            self.assertIn('My tasks', html)
            self.assertIn('data-urgent="true"', html)
            self.assertNotIn('All documents', html)
            self.assertEqual(self.get_counts(), {'todo': 42})
        finally:
            site_manager.unregisterAdapter(ProjectBoxesProvider)


class TestProjectBoxesProvider(DashboardBoxesProviderContract, InteraktivBasetilesTestCase):
    """ the adapter of a project is checked with the same contract tests """
    layer = GRAFFITI_TILE_DASHBOARD_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        getGlobalSiteManager().registerAdapter(ProjectBoxesProvider)
        alsoProvides(self.request, IProjectLayer)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(ProjectBoxesProvider)
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.tilepage, self.request), IDashboardBoxesProvider)
