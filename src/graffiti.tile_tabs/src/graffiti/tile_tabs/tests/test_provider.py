import plone.api as api
from DateTime import DateTime
from graffiti.tile_tabs.contract import TabListsProviderContract
from graffiti.tile_tabs.interfaces import ITabListsProvider
from graffiti.tile_tabs.testing import GRAFFITI_TILE_TABS_FUNCTIONAL_TESTING
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, logout, setRoles
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter, getGlobalSiteManager, getMultiAdapter
from zope.interface import Interface, alsoProvides, implementer


class IProjectLayer(Interface):
    """ request layer of a project that delivers its own tabs """


@implementer(ITabListsProvider)
@adapter(ITilePage, IProjectLayer)
class ProjectTabsProvider:

    def __init__(self, context, request):
        pass

    def get_tabs(self):
        columns = [{'id': 'name', 'title': 'Name'}, {'id': 'hits', 'title': 'Hits'}]
        return [
            {'id': 'saved', 'title': 'My saved searches', 'columns': columns, 'empty_text': 'Nothing saved',
             'rows': [{'url': 'http://nohost/saved/1', 'cells': {'name': 'Open tasks', 'hits': '12'}}]},
            {'id': 'favorites', 'title': 'Favorites', 'columns': columns, 'empty_text': 'No favorites', 'rows': []},
        ]


class TestDefaultTabsProvider(TabListsProviderContract, InteraktivBasetilesTestCase):
    """ the default adapter fulfils the contract """
    layer = GRAFFITI_TILE_TABS_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        self.folder = api.content.create(container=self.portal, type='Folder', id='entry', title='Entry')
        self.entry_page = self.create_tilepage(_id='entry-page', container=self.folder, title='Entry page')
        api.content.create(container=self.folder, type='Document', id='doc-a', title='Document A')
        api.content.create(container=self.portal, type='Document', id='doc-outside', title='Document outside')
        api.content.create(
            container=self.folder, type='Document', id='doc-hidden', title='Document hidden', exclude_from_nav=True
        )

    def tearDown(self):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.delete(self.portal, self.folder)
        self.delete(self.portal, 'doc-outside')
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.entry_page, self.request), ITabListsProvider)

    def get_tab(self, tab_id):
        return [tab for tab in self.get_provider().get_tabs() if tab['id'] == tab_id][0]

    def titles(self, tab):
        return [row['cells']['title'] for row in tab['rows']]

    def test_default_has_three_tabs_with_the_same_columns(self):
        tabs = self.get_provider().get_tabs()

        self.assertEqual([tab['id'] for tab in tabs], ['recent', 'mine', 'folder'])
        for tab in tabs:
            self.assertEqual([column['id'] for column in tab['columns']], ['title', 'type', 'modified'])

    def test_recent_lists_newest_first_with_type_and_date(self):
        # the index "modified" has a resolution of one minute, so the order needs a clear gap
        self.folder['doc-a'].setModificationDate(DateTime() - 2)
        self.folder['doc-a'].reindexObject(idxs=['modified'])
        tab = self.get_tab('recent')
        titles = self.titles(tab)

        self.assertLess(titles.index('Document hidden'), titles.index('Document A'))
        self.assertNotIn('Plone site', titles)
        row = tab['rows'][titles.index('Document A')]
        self.assertEqual(row['url'], self.folder['doc-a'].absolute_url())
        self.assertEqual(row['cells']['type'], 'Page')
        self.assertTrue(row['cells']['modified'])

    def test_recent_is_limited_to_ten_rows(self):
        for number in range(12):
            api.content.create(container=self.folder, type='Document', id=f'doc-{number}', title=f'Doc {number}')

        self.assertEqual(len(self.get_tab('recent')['rows']), 10)

    def test_mine_lists_content_of_the_current_user_only(self):
        self.assertIn('Document A', self.titles(self.get_tab('mine')))

        logout()
        self.assertEqual(self.get_tab('mine')['rows'], [])

    def test_folder_lists_folder_content_without_page_and_hidden_items(self):
        self.assertEqual(self.titles(self.get_tab('folder')), ['Document A'])


class TestProjectTabsProvider(TabListsProviderContract, InteraktivBasetilesTestCase):
    """ a project replaces the adapter for its own request layer """
    layer = GRAFFITI_TILE_TABS_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        getGlobalSiteManager().registerAdapter(ProjectTabsProvider)
        alsoProvides(self.request, IProjectLayer)

    def tearDown(self):
        getGlobalSiteManager().unregisterAdapter(ProjectTabsProvider)
        super().tearDown()

    def get_provider(self):
        return getMultiAdapter((self.tilepage, self.request), ITabListsProvider)

    def test_tile_renders_tabs_of_the_project(self):
        edit_rows = IAnnotations(self.tilepage)['edit']['tiles']
        tile_row = self.tilepage.create_tilerow(container=edit_rows)
        tile = self.tilepage.create_tile(container=tile_row, portaltype='TileTabs', title='Lists')

        html = self.tilepage.render(tile)

        self.assertIn('My saved searches', html)
        self.assertIn('href="http://nohost/saved/1"', html)
        self.assertIn('Open tasks', html)
        self.assertIn('No favorites', html)
