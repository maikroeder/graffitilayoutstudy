from graffiti.tile_dashboard.testing import GRAFFITI_TILE_DASHBOARD_INTEGRATION_TESTING
from interaktiv.basetiles.base_functions import get_registered_tiles
from interaktiv.framework.test import TestCase


class TestSetup(TestCase):
    layer = GRAFFITI_TILE_DASHBOARD_INTEGRATION_TESTING
    product_name = 'graffiti.tile_dashboard'

    def test_product_installed(self):
        self.assertTrue(self.is_product_installed(self.product_name))

    def test_tile_registered_in_editor(self):
        portal_types = [tile['portaltype'] for tile in get_registered_tiles()]
        self.assertIn('TileDashboard', portal_types)


class TestUninstall(TestCase):
    layer = GRAFFITI_TILE_DASHBOARD_INTEGRATION_TESTING
    product_name = 'graffiti.tile_dashboard'

    def test_product_uninstalled(self):
        self.uninstall_product(self.product_name)
        self.assertFalse(self.is_product_installed(self.product_name))
