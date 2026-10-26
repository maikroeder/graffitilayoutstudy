from interaktiv.framework import TestLayer
from plone.app.testing import FunctionalTesting, IntegrationTesting


class GraffitiPdfcheckLayer(TestLayer):

    def __init__(self):
        super().__init__()
        self.products_to_import = [
            'plone.app.contenttypes',
            'plone.restapi',
            'interaktiv.framework',
            'graffiti.pdfcheck'
        ]
        self.product_to_install = 'graffiti.pdfcheck'
        # the content type File and the REST API
        self.products_optional = [
            'plone.app.contenttypes',
            'plone.restapi'
        ]


GRAFFITI_PDFCHECK_FIXTURE = GraffitiPdfcheckLayer()
GRAFFITI_PDFCHECK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_PDFCHECK_FIXTURE,),
    name="GraffitiPdfcheckLayer:Integration"
)
GRAFFITI_PDFCHECK_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_PDFCHECK_FIXTURE,),
    name="GraffitiPdfcheckLayer:Functional"
)
