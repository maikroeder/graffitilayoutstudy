from graffiti.tile_button.interfaces import IGraffitiTileButtonLayer
from graffiti.tile_button.testing import GRAFFITI_TILE_BUTTON_INTEGRATION_TESTING
from interaktiv.framework.test import TestCase
from plone.browserlayer.utils import registered_layers
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

BEHAVIOR = 'graffiti.tile_button.behaviors.IButtonCssClassesBehavior'


class TestSetup(TestCase):
    layer = GRAFFITI_TILE_BUTTON_INTEGRATION_TESTING
    product_name = 'graffiti.tile_button'

    def test_product_installed(self):
        self.assertTrue(self.is_product_installed(self.product_name))

    def test_browserlayer_registered(self):
        self.assertIn(IGraffitiTileButtonLayer, registered_layers())

    def test_switch_in_registry(self):
        self.assertTrue(getUtility(IRegistry)['graffiti.tile_button.css_classes_enabled'])

    def test_behavior_on_button_tile(self):
        self.assertIn(BEHAVIOR, self.portal.portal_types['TileButtonCT'].behaviors)


class TestUninstall(TestCase):
    layer = GRAFFITI_TILE_BUTTON_INTEGRATION_TESTING
    product_name = 'graffiti.tile_button'

    def test_product_uninstalled(self):
        self.uninstall_product(self.product_name)
        self.assertFalse(self.is_product_installed(self.product_name))
        self.assertNotIn(IGraffitiTileButtonLayer, registered_layers())
        self.assertNotIn(BEHAVIOR, self.portal.portal_types['TileButtonCT'].behaviors)
        self.assertNotIn('graffiti.tile_button.css_classes_enabled', getUtility(IRegistry))
