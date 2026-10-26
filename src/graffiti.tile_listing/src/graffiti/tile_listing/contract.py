""" Contract of the extension point `IListingItemsProvider` as reusable tests.

A project that delivers its own entries checks its adapter like this:

    class TestMyItems(ListingItemsProviderContract, MyTestCase):

        def get_provider(self):
            return getMultiAdapter((self.tilepage, self.request), IListingItemsProvider)
"""
from graffiti.tile_listing.interfaces import IListingItemsProvider
from zope.interface.verify import verifyObject

ITEM_KEYS = {'title', 'description', 'url', 'portal_type'}


class ListingItemsProviderContract:
    """ Mixin for a `unittest.TestCase` """

    def get_provider(self) -> IListingItemsProvider:
        raise NotImplementedError('return the adapter that should be checked')

    def test_contract_provider_provides_interface(self):
        self.assertTrue(verifyObject(IListingItemsProvider, self.get_provider()))

    def test_contract_label_is_a_string(self):
        self.assertIsInstance(self.get_provider().get_label(), str)

    def test_contract_items_have_all_keys_as_strings(self):
        for item in self.get_provider().get_items():
            self.assertEqual(set(item.keys()), ITEM_KEYS)
            for key in ITEM_KEYS:
                self.assertIsInstance(item[key], str, f'item["{key}"]')
            self.assertTrue(item['title'])
            self.assertTrue(item['url'])
