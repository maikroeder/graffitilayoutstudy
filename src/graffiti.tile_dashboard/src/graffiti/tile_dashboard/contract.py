""" Contract of the extension point `IDashboardBoxesProvider` as reusable tests.

A project that delivers its own boxes checks its adapter like this:

    class TestMyBoxes(DashboardBoxesProviderContract, MyTestCase):

        def get_provider(self):
            return getMultiAdapter((self.tilepage, self.request), IDashboardBoxesProvider)
"""
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from zope.interface.verify import verifyObject

BOX_KEYS = {'id', 'title', 'description', 'url'}
OPTIONAL_BOX_KEYS = {'urgent'}


class DashboardBoxesProviderContract:
    """ Mixin for a `unittest.TestCase` """

    def get_provider(self) -> IDashboardBoxesProvider:
        raise NotImplementedError('return the adapter that should be checked')

    def test_contract_provider_provides_interface(self):
        self.assertTrue(verifyObject(IDashboardBoxesProvider, self.get_provider()))

    def test_contract_boxes_have_all_keys_as_strings(self):
        for box in self.get_provider().get_boxes():
            self.assertEqual(set(box.keys()) - OPTIONAL_BOX_KEYS, BOX_KEYS)
            for key in BOX_KEYS:
                self.assertIsInstance(box[key], str, f'box["{key}"]')
            self.assertTrue(box['id'])
            self.assertTrue(box['title'])

    def test_contract_urgent_is_optional_and_a_bool(self):
        for box in self.get_provider().get_boxes():
            if 'urgent' in box:
                self.assertIsInstance(box['urgent'], bool, f'box["urgent"] of "{box["id"]}"')

    def test_contract_box_ids_are_unique(self):
        ids = [box['id'] for box in self.get_provider().get_boxes()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_contract_counts_match_boxes(self):
        provider = self.get_provider()
        ids = {box['id'] for box in provider.get_boxes()}
        counts = provider.get_counts()

        self.assertEqual(set(counts.keys()), ids)
        for box_id, count in counts.items():
            self.assertIsInstance(count, int, f'count of "{box_id}"')
            self.assertGreaterEqual(count, 0)
