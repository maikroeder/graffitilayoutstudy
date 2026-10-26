from graffiti.testing.testing import GraffitiTestingLayer

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiSearchLayer(GraffitiTestingLayer):
    additional_products_to_import = []
    additional_products_to_install = [
        'graffiti.search'
    ]


GRAFFITI_SEARCH_FIXTURE = GraffitiSearchLayer()
GRAFFITI_SEARCH_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_SEARCH_FIXTURE,),
    name="GraffitiSearchLayer:Integration"
)
GRAFFITI_SEARCH_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_SEARCH_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiSearchLayer:Functional"
)
