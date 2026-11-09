"""Unit tests of the body class adapter and the layout list. No Plone site is needed, only the packages
the code imports (Acquisition, zope.component, plone.app.layout)."""
import unittest

from Acquisition import Implicit
from openheidelberg.theme.body_classes import OpenHeidelbergBodyClasses
from openheidelberg.theme.layouts import LAYOUT_SITE_SEARCH
from openheidelberg.theme.layouts import LAYOUTS
from openheidelberg.theme.layouts import layout_ids
from openheidelberg.theme.layouts import page_layouts_vocabulary
from plone.app.layout.globals.interfaces import IBodyClassAdapter
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.interface import alsoProvides


class FakeRequest:
    pass


class FakeContextState:
    """Stands for the view plone_context_state."""

    default_view = True

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_view_template(self):
        return FakeContextState.default_view


class FakeContainer(Implicit):

    def __init__(self, default_page=None):
        self.default_page = default_page

    def getDefaultPage(self):
        return self.default_page


class FakeItem(Implicit):

    def __init__(self, item_id, page_layout=None):
        self.item_id = item_id
        if page_layout is not None:
            self.page_layout = page_layout

    def getId(self):
        return self.item_id


def make_root(default_page=None):
    root = FakeContainer(default_page)
    alsoProvides(root, INavigationRoot)
    return root


def make_adapter(item):
    return OpenHeidelbergBodyClasses(item, FakeRequest())


class AdapterTestCase(unittest.TestCase):

    def setUp(self):
        FakeContextState.default_view = True
        self.manager = getGlobalSiteManager()
        self.manager.registerAdapter(FakeContextState, (Interface, Interface), Interface, 'plone_context_state')

    def tearDown(self):
        self.manager.unregisterAdapter(FakeContextState, (Interface, Interface), Interface, 'plone_context_state')


class TestConfiguredLayout(AdapterTestCase):

    def test_value_of_the_field(self):
        root = make_root()
        item = FakeItem('about', LAYOUT_SITE_SEARCH).__of__(root)
        self.assertEqual(make_adapter(item).get_configured_layout(), LAYOUT_SITE_SEARCH)

    def test_value_of_the_field_wins_without_a_root(self):
        item = FakeItem('about', LAYOUT_SITE_SEARCH)
        self.assertEqual(make_adapter(item).get_configured_layout(), LAYOUT_SITE_SEARCH)

    def test_default_page_of_the_navigation_root(self):
        root = make_root('start')
        item = FakeItem('start').__of__(root)
        self.assertEqual(make_adapter(item).get_configured_layout(), LAYOUT_SITE_SEARCH)

    def test_other_page_of_the_navigation_root(self):
        root = make_root('start')
        item = FakeItem('about').__of__(root)
        self.assertIsNone(make_adapter(item).get_configured_layout())

    def test_root_without_default_page(self):
        root = make_root(None)
        item = FakeItem('start').__of__(root)
        self.assertIsNone(make_adapter(item).get_configured_layout())

    def test_default_page_of_a_folder_that_is_not_a_navigation_root(self):
        folder = FakeContainer('start')
        item = FakeItem('start').__of__(folder)
        self.assertIsNone(make_adapter(item).get_configured_layout())

    def test_unknown_value_is_ignored(self):
        root = make_root('start')
        item = FakeItem('about', 'no-such-layout').__of__(root)
        self.assertIsNone(make_adapter(item).get_configured_layout())

    def test_unknown_value_on_the_default_page_falls_back_to_the_root_rule(self):
        root = make_root('start')
        item = FakeItem('start', 'no-such-layout').__of__(root)
        self.assertEqual(make_adapter(item).get_configured_layout(), LAYOUT_SITE_SEARCH)

    def test_removed_layout_value_is_ignored(self):
        root = make_root('start')
        item = FakeItem('about', 'default-tiles-layout').__of__(root)
        self.assertIsNone(make_adapter(item).get_configured_layout())

    def test_empty_value_is_ignored(self):
        root = make_root('start')
        item = FakeItem('about', '').__of__(root)
        self.assertIsNone(make_adapter(item).get_configured_layout())

    def test_acquired_value_is_not_used(self):
        # page_layout must be set on the object itself; a value on a parent must not be acquired
        root = make_root('start')
        root.page_layout = LAYOUT_SITE_SEARCH
        item = FakeItem('about').__of__(root)
        self.assertIsNone(make_adapter(item).get_configured_layout())


class TestGetClasses(AdapterTestCase):

    def test_class_for_the_configured_layout_in_the_default_view(self):
        root = make_root()
        item = FakeItem('about', LAYOUT_SITE_SEARCH).__of__(root)
        classes = make_adapter(item).get_classes(None, None)
        self.assertEqual(classes, {'layout-site-search-layout'})

    def test_class_for_the_default_page_of_the_root(self):
        root = make_root('start')
        item = FakeItem('start').__of__(root)
        self.assertEqual(make_adapter(item).get_classes(None, None), {'layout-site-search-layout'})

    def test_no_class_outside_the_default_view(self):
        # edit form, tiles editor, @@sharing, @@manage-portlets
        FakeContextState.default_view = False
        root = make_root('start')
        item = FakeItem('start', LAYOUT_SITE_SEARCH).__of__(root)
        self.assertEqual(make_adapter(item).get_classes(None, None), set())

    def test_no_class_without_a_layout(self):
        root = make_root('start')
        item = FakeItem('about').__of__(root)
        self.assertEqual(make_adapter(item).get_classes(None, None), set())

    def test_result_is_a_set_that_the_policy_can_merge(self):
        root = make_root('start')
        item = FakeItem('start').__of__(root)
        classes = make_adapter(item).get_classes(None, None)
        self.assertIsInstance(classes, set)
        for name in classes:
            self.assertIsInstance(name, str)
            self.assertNotIn(' ', name)

    def test_is_default_view_follows_the_context_state(self):
        item = FakeItem('about')
        adapter = make_adapter(item)
        self.assertTrue(adapter.is_default_view())
        FakeContextState.default_view = False
        self.assertFalse(adapter.is_default_view())

    def test_implements_the_adapter_interface(self):
        self.assertTrue(IBodyClassAdapter.implementedBy(OpenHeidelbergBodyClasses))
        adapter = make_adapter(FakeItem('about'))
        self.assertTrue(IBodyClassAdapter.providedBy(adapter))


class TestLayouts(unittest.TestCase):

    def test_ids(self):
        self.assertEqual(layout_ids(), [LAYOUT_SITE_SEARCH])
        self.assertEqual(LAYOUT_SITE_SEARCH, 'site-search-layout')

    def test_ids_are_usable_as_body_class_suffix(self):
        for layout_id in layout_ids():
            self.assertRegex(layout_id, r'^[a-z0-9-]+$')

    def test_layouts_list_has_a_title_for_each_id(self):
        for layout_id, title in LAYOUTS:
            self.assertTrue(layout_id)
            self.assertTrue(title)

    def test_vocabulary(self):
        vocabulary = page_layouts_vocabulary(None)
        self.assertEqual(len(vocabulary), len(LAYOUTS))
        term = vocabulary.getTerm(LAYOUT_SITE_SEARCH)
        self.assertEqual(term.value, LAYOUT_SITE_SEARCH)
        self.assertEqual(term.token, LAYOUT_SITE_SEARCH)
        self.assertIn(LAYOUT_SITE_SEARCH, vocabulary)
        self.assertNotIn('default-tiles-layout', vocabulary)


if __name__ == '__main__':
    unittest.main()
