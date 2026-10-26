from interaktiv.framework.test import TestCase
from graffiti.testing.testing import GraffitiTestingLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing.zope import WSGI_SERVER_FIXTURE
from plone.testing.zope import installProduct
from zExceptions import Unauthorized


class GraffitiPolicyLayer(GraffitiTestingLayer):
    additional_products_to_import = [
        'graffiti.contenttypes',
        'graffiti.tile_listing',
        'graffiti.tile_search',
        'graffiti.tile_dashboard',
        'graffiti.tile_tabs',
        'graffiti.tile_view',
        'graffiti.tile_button',
        'graffiti.pdfcheck',
        'plone.app.iterate',

        'interaktiv.framework',
        'interaktiv.fonts',
        'interaktiv.image_focus',
        'interaktiv.migrator',
        'interaktiv.workingcopy',
        'interaktiv.layout',

        'interaktiv.basetiles',
        'interaktiv.tile_image',
        'interaktiv.tile_text',
        'interaktiv.tile_files',
        'interaktiv.tile_subheadline',
        'interaktiv.tile_news',
        'interaktiv.tile_audio',
        'interaktiv.tile_button',
        'interaktiv.tile_collapse',
        'interaktiv.tile_contact',
        'interaktiv.tile_icon',
        'interaktiv.tile_iframe',
        'interaktiv.tile_line',
        'interaktiv.tile_map',
        'interaktiv.tile_slider',
        'interaktiv.tile_spacer',
        'interaktiv.tile_timeline',
        'interaktiv.tile_video',
        'interaktiv.tilepage_versioning',
        'interaktiv.theme',
    ]
    additional_products_to_install = [
        'graffiti.policy'
    ]


GRAFFITI_POLICY_FIXTURE = GraffitiPolicyLayer()
GRAFFITI_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GRAFFITI_POLICY_FIXTURE,),
    name="GraffitiPolicyLayer:Integration"
)
GRAFFITI_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GRAFFITI_POLICY_FIXTURE, WSGI_SERVER_FIXTURE),
    name="GraffitiPolicyLayer:Functional"
)
