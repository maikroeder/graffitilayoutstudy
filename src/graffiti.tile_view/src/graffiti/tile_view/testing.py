from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiTileViewLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'interaktiv.framework',
            'interaktiv.basetiles',
            'graffiti.tile_view'
        ]
        self.product_to_install = 'graffiti.tile_view'


GRAFFITI_TILE_VIEW_FIXTURE = GraffitiTileViewLayer()
GRAFFITI_TILE_VIEW_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_TILE_VIEW_FIXTURE,),
    name="GraffitiTileViewLayer:Integration"
)
GRAFFITI_TILE_VIEW_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_TILE_VIEW_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiTileViewLayer:Functional"
)
