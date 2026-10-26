from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiTileListingLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'interaktiv.framework',
            'interaktiv.basetiles',
            'graffiti.tile_listing'
        ]
        self.product_to_install = 'graffiti.tile_listing'


GRAFFITI_TILE_LISTING_FIXTURE = GraffitiTileListingLayer()
GRAFFITI_TILE_LISTING_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_TILE_LISTING_FIXTURE,),
    name="GraffitiTileListingLayer:Integration"
)
GRAFFITI_TILE_LISTING_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_TILE_LISTING_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiTileListingLayer:Functional"
)
