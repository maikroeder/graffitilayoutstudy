""" Contract of the extension point `ITabListsProvider` as reusable tests.

A project that delivers its own tabs checks its adapter like this:

    class TestMyTabs(TabListsProviderContract, MyTestCase):

        def get_provider(self):
            return getMultiAdapter((self.tilepage, self.request), ITabListsProvider)
"""
from graffiti.tile_tabs.interfaces import ITabListsProvider
from zope.interface.verify import verifyObject

TAB_KEYS = {'id', 'title', 'columns', 'rows', 'empty_text'}
COLUMN_KEYS = {'id', 'title'}
ROW_KEYS = {'url', 'cells'}


class TabListsProviderContract:
    """ Mixin for a `unittest.TestCase` """

    def get_provider(self) -> ITabListsProvider:
        raise NotImplementedError('return the adapter that should be checked')

    def test_contract_provider_provides_interface(self):
        self.assertTrue(verifyObject(ITabListsProvider, self.get_provider()))

    def test_contract_tabs_have_all_keys_and_unique_ids(self):
        tabs = self.get_provider().get_tabs()
        for tab in tabs:
            self.assertEqual(set(tab.keys()), TAB_KEYS)
            for key in ('id', 'title', 'empty_text'):
                self.assertIsInstance(tab[key], str, f'tab["{key}"]')
            self.assertTrue(tab['id'])
            self.assertTrue(tab['title'])
        self.assertEqual(len({tab['id'] for tab in tabs}), len(tabs), 'tab ids are not unique')

    def test_contract_columns_have_id_and_title(self):
        for tab in self.get_provider().get_tabs():
            columns = tab['columns']
            self.assertTrue(columns, f'tab "{tab["id"]}" has no columns')
            for column in columns:
                self.assertEqual(set(column.keys()), COLUMN_KEYS)
                self.assertIsInstance(column['id'], str)
                self.assertIsInstance(column['title'], str)
                self.assertTrue(column['id'])
            self.assertEqual(len({column['id'] for column in columns}), len(columns), 'column ids are not unique')

    def test_contract_rows_have_url_and_cells_matching_columns(self):
        for tab in self.get_provider().get_tabs():
            column_ids = {column['id'] for column in tab['columns']}
            for row in tab['rows']:
                self.assertEqual(set(row.keys()), ROW_KEYS)
                self.assertIsInstance(row['url'], str)
                self.assertIsInstance(row['cells'], dict)
                self.assertTrue(set(row['cells'].keys()) <= column_ids, f'cells outside the columns: {row["cells"]}')
                for value in row['cells'].values():
                    self.assertIsInstance(value, str)
