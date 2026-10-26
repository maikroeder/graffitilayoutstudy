from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiTileDashboardLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'interaktiv.framework',
            'interaktiv.basetiles',
            'graffiti.tile_dashboard'
        ]
        self.product_to_install = 'graffiti.tile_dashboard'


GRAFFITI_TILE_DASHBOARD_FIXTURE = GraffitiTileDashboardLayer()
GRAFFITI_TILE_DASHBOARD_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_TILE_DASHBOARD_FIXTURE,),
    name="GraffitiTileDashboardLayer:Integration"
)
GRAFFITI_TILE_DASHBOARD_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_TILE_DASHBOARD_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiTileDashboardLayer:Functional"
)
