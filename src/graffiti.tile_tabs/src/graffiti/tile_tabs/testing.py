from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiTileTabsLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'interaktiv.framework',
            'interaktiv.basetiles',
            'graffiti.tile_tabs'
        ]
        self.product_to_install = 'graffiti.tile_tabs'


GRAFFITI_TILE_TABS_FIXTURE = GraffitiTileTabsLayer()
GRAFFITI_TILE_TABS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_TILE_TABS_FIXTURE,),
    name="GraffitiTileTabsLayer:Integration"
)
GRAFFITI_TILE_TABS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_TILE_TABS_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiTileTabsLayer:Functional"
)
