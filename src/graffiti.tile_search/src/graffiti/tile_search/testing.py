from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiTileSearchLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'interaktiv.framework',
            'interaktiv.basetiles',
            'graffiti.tile_search'
        ]
        self.product_to_install = 'graffiti.tile_search'


GRAFFITI_TILE_SEARCH_FIXTURE = GraffitiTileSearchLayer()
GRAFFITI_TILE_SEARCH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_TILE_SEARCH_FIXTURE,),
    name="GraffitiTileSearchLayer:Integration"
)
GRAFFITI_TILE_SEARCH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_TILE_SEARCH_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiTileSearchLayer:Functional"
)
