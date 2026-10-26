from graffiti.testing.testing import GraffitiTestingLayer

from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE


class GraffitiContenttypesLayer(GraffitiTestingLayer):
    additional_products_to_import = []
    additional_products_to_install = [
        'graffiti.contenttypes'
    ]


GRAFFITI_CONTENTTYPES_FIXTURE = GraffitiContenttypesLayer()
GRAFFITI_CONTENTTYPES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_CONTENTTYPES_FIXTURE,),
    name="GraffitiContenttypesLayer:Integration"
)
GRAFFITI_CONTENTTYPES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_CONTENTTYPES_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiContenttypesLayer:Functional"
)
