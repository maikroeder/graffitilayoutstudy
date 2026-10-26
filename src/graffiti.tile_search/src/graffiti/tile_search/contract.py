""" Contract of the extension point `ISearchTileSettings` as reusable tests.

A project that uses its own search checks its adapter like this:

    class TestMySearchSettings(SearchTileSettingsContract, MyTestCase):

        def get_settings(self):
            return getMultiAdapter((self.tilepage, self.request), ISearchTileSettings)
"""
from graffiti.tile_search.interfaces import ISearchTileSettings
from zope.interface.verify import verifyObject


class SearchTileSettingsContract:
    """ Mixin for a `unittest.TestCase` """

    def get_settings(self) -> ISearchTileSettings:
        raise NotImplementedError('return the adapter that should be checked')

    def test_contract_settings_provide_interface(self):
        self.assertTrue(verifyObject(ISearchTileSettings, self.get_settings()))

    def test_contract_search_url_is_absolute(self):
        search_url = self.get_settings().get_search_url()
        self.assertIsInstance(search_url, str)
        self.assertTrue(search_url.startswith(('http://', 'https://')), search_url)

    def test_contract_livesearch_url_is_absolute_or_none(self):
        livesearch_url = self.get_settings().get_livesearch_url()
        if livesearch_url is not None:
            self.assertIsInstance(livesearch_url, str)
            self.assertTrue(livesearch_url.startswith(('http://', 'https://')), livesearch_url)

    def test_contract_parameters_are_strings(self):
        parameters = self.get_settings().get_parameters()
        self.assertIsInstance(parameters, dict)
        for name, value in parameters.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(value, str)
        self.assertNotIn('SearchableText', parameters)

    def test_contract_search_parameter_name_is_a_plain_name(self):
        name = self.get_settings().get_search_parameter_name()
        self.assertIsInstance(name, str)
        self.assertTrue(name)
        self.assertNotIn(' ', name)
        self.assertNotIn(name, self.get_settings().get_parameters())
