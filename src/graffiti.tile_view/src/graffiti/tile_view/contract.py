""" Contract of the extension point `IEmbeddableViewsProvider` as reusable tests.

A project that registers its own views checks its adapter like this:

    class TestMyViews(EmbeddableViewsContract, MyTestCase):

        def get_provider(self):
            return getMultiAdapter((self.tilepage, self.request), IEmbeddableViewsProvider)
"""
from graffiti.tile_view.embed import render_entry
from graffiti.tile_view.interfaces import IEmbeddableViewsProvider, MODES
from zope.interface.verify import verifyObject

ENTRY_KEYS = {'id', 'title', 'description', 'url', 'mode'}


class EmbeddableViewsContract:
    """ Mixin for a `unittest.TestCase` """

    def get_provider(self) -> IEmbeddableViewsProvider:
        raise NotImplementedError('return the adapter that should be checked')

    def test_contract_provider_provides_interface(self):
        self.assertTrue(verifyObject(IEmbeddableViewsProvider, self.get_provider()))

    def test_contract_entries_have_all_keys(self):
        for entry in self.get_provider().get_views():
            self.assertEqual(set(entry.keys()), ENTRY_KEYS)
            for key in ENTRY_KEYS:
                self.assertIsInstance(entry[key], str, f'entry["{key}"]')
            self.assertTrue(entry['id'])
            self.assertTrue(entry['title'])
            self.assertTrue(entry['url'].startswith(('http://', 'https://')), entry['url'])
            self.assertIn(entry['mode'], MODES)

    def test_contract_ids_are_unique(self):
        ids = [entry['id'] for entry in self.get_provider().get_views()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_contract_every_entry_renders_a_fragment(self):
        for entry in self.get_provider().get_views():
            html = render_entry(entry, self.request)
            self.assertTrue(html, f'view "{entry["id"]}" renders nothing')
            self.assertNotIn('<html', html.lower(), f'view "{entry["id"]}" renders a whole page')
            self.assertNotIn('id="content"', html, f'view "{entry["id"]}" contains the page frame')
