from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiTileButtonLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'interaktiv.framework',
            'interaktiv.basetiles',
            'interaktiv.fonts',
            'interaktiv.tile_button',
            'graffiti.tile_button'
        ]
        self.product_to_install = 'graffiti.tile_button'


GRAFFITI_TILE_BUTTON_FIXTURE = GraffitiTileButtonLayer()
GRAFFITI_TILE_BUTTON_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_TILE_BUTTON_FIXTURE,),
    name="GraffitiTileButtonLayer:Integration"
)
GRAFFITI_TILE_BUTTON_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_TILE_BUTTON_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiTileButtonLayer:Functional"
)
