import unittest
from copy import deepcopy

import plone.api as api
from graffiti.tile_button.css_classes import InvalidCssClasses
from graffiti.tile_button.css_classes import check_css_classes
from graffiti.tile_button.css_classes import split_css_classes
from graffiti.tile_button.interfaces import IGraffitiTileButtonLayer
from graffiti.tile_button.testing import GRAFFITI_TILE_BUTTON_FUNCTIONAL_TESTING
from graffiti.tile_button.views.view import TileButtonView
from interaktiv.basetiles.permissions import InteraktivBasetilesTileStyle
from interaktiv.basetiles.test import InteraktivBasetilesTestCase
from interaktiv.tile_button.permissions import InteraktivBasetilesTileButtonStyle
from interaktiv.tile_button.views.view import TileButtonCTView
from zExceptions import Unauthorized
from zope.interface import alsoProvides


class TestCssClassesValidation(unittest.TestCase):

    def test_check_css_classes_accepts_valid_values(self):
        for value in (None, '', '   ', 'open-dialog', 'a B_1 c-2', '  spaced   out  '):
            self.assertTrue(check_css_classes(value), value)

    def test_check_css_classes_rejects_invalid_values(self):
        for value in ('a"b', 'a;b', '"><script>', 'a.b', 'a:b', 'klasse-ä', 'a,b'):
            with self.assertRaises(InvalidCssClasses, msg=value):
                check_css_classes(value)

    def test_split_css_classes_drops_invalid_classes(self):
        self.assertEqual(split_css_classes(None), [])
        self.assertEqual(split_css_classes('  one  two '), ['one', 'two'])
        self.assertEqual(split_css_classes('ok "><script> also_ok'), ['ok', 'also_ok'])


class ButtonTestCase(InteraktivBasetilesTestCase):
    layer = GRAFFITI_TILE_BUTTON_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()
        alsoProvides(self.request, IGraffitiTileButtonLayer)
        self.tile = self.tilepage.create_tile(
            container=self.tilerow,
            portaltype='TileButtonCT',
            **{'title': 'Tile Button', 'button_text': 'Create document'}
        )

    def get_view(self):
        view = api.content.get_view(name=self.tile['view_name'], context=self.tilepage, request=self.request)
        view(self.tile)
        return view

    def remove_style_permission(self):
        self.portal.manage_permission(permission_to_manage=InteraktivBasetilesTileStyle, roles=[])
        self.portal.manage_permission(permission_to_manage=InteraktivBasetilesTileButtonStyle, roles=[])


class TestButtonView(ButtonTestCase):

    def test_template_for_the_installed_version(self):
        """ Fails for a version of interaktiv.tile_button without a copy of its template in this package,
        the button tile would render without the custom classes """
        from graffiti.tile_button.views.view import TEMPLATE, TILE_BUTTON_VERSION
        self.assertIsNotNone(TEMPLATE, 'no template for interaktiv.tile_button ' + TILE_BUTTON_VERSION)

    def test_view_of_this_package_is_used(self):
        self.assertIsInstance(self.get_view(), TileButtonView)

    def test_button_classes_default(self):
        self.assertEqual(self.get_view().get_button_classes(), 'button')

    def test_button_classes_are_rendered(self):
        self.tile['button_css_classes'] = 'open-dialog  primary'
        view = self.get_view()
        self.assertEqual(view.get_button_classes(), 'button open-dialog primary')
        self.assertIn('class="button open-dialog primary"', view(self.tile))

    def test_template_matches_the_original(self):
        """ The template is a copy of the one of interaktiv.tile_button. If this test fails after an
        update of interaktiv.tile_button, compare views/templates/view.pt with the new original. """
        self.tile['button_css_classes'] = 'open-dialog primary'
        # rendering adds default values to the tile, so both views get the same copy
        original_html = TileButtonCTView(self.tilepage, self.request)(deepcopy(self.tile))
        own_html = TileButtonView(self.tilepage, self.request)(deepcopy(self.tile))
        self.assertIn('class="button"', original_html)
        self.assertEqual(own_html.replace('class="button open-dialog primary"', 'class="button"'), original_html)


class TestSaving(ButtonTestCase):

    def test_update_element_sets_css_classes(self):
        self.tilepage.update_element(self.tile, {'button_css_classes': 'open-dialog primary'})
        self.assertEqual(self.tile['button_css_classes'], 'open-dialog primary')

    def test_update_element_rejects_invalid_css_classes(self):
        with self.assertRaises(InvalidCssClasses):
            self.tilepage.update_element(self.tile, {'button_css_classes': 'open-dialog" onclick="alert(1)'})
        self.assertFalse(self.tile.get('button_css_classes'))

    def test_update_element_needs_style_permission(self):
        self.remove_style_permission()
        with self.assertRaises(Unauthorized):
            self.tilepage.update_element(self.tile, {'button_css_classes': 'open-dialog'})
        # the dialog of the button tile keeps working
        self.tilepage.update_element(self.tile, {'button_text': 'New text'})
        self.assertEqual(self.tile['button_text'], 'New text')
