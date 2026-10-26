# -*- coding: UTF-8 -*-
import importlib
import os

import interaktiv.framework as framework
from Products.CMFCore.utils import getToolByName
from plone.app.contenttypes.interfaces import IDocument
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.dexterity import utils
from plone.testing.zope import WSGI_SERVER_FIXTURE
from zope.configuration import xmlconfig

os.environ['PLONE_CSRF_DISABLED'] = 'true'


class InteraktivWorkingcopyLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)
    products_to_import = [
        'plone.app.contenttypes',
        'plone.app.iterate',
        'interaktiv.workingcopy'
    ]

    def setUpZope(self, app, configuration_context):
        for product_name in self.products_to_import:
            module = importlib.import_module(product_name)
            xmlconfig.file(
                'configure.zcml',
                module,
                context=configuration_context
            )

    @staticmethod
    def _set_workingcopy_behavior_for_document(portal):
        behavior = "interaktiv.workingcopy.behaviors." \
                   "workingcopy.IWorkingcopyBehavior"
        #
        ftis = []
        types_tool = getToolByName(portal, 'portal_types')
        for fti in types_tool.listTypeInfo():
            if not hasattr(fti, 'klass'):
                continue
            klass = utils.resolveDottedName(fti.klass)
            if IDocument.implementedBy(klass):
                ftis.append(fti)
                continue
        #
        for fti in ftis:
            if behavior in fti.behaviors:
                continue
            behaviors = list(fti.behaviors)
            behaviors.append(behavior)

            fti._updateProperty('behaviors', tuple(behaviors))

    def setUpPloneSite(self, portal):
        for product_name in self.products_to_import:
            applyProfile(portal, product_name + ':default')
        self._set_workingcopy_behavior_for_document(portal)
        # set workflow for portal type
        framework.workflow.set_workflow(
            portal_types=['Document'],
            workflow_name='simple_publication_workflow'
        )


INTERAKTIV_WORKINGCOPY_FIXTURE = InteraktivWorkingcopyLayer()
INTERAKTIV_WORKINGCOPY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(INTERAKTIV_WORKINGCOPY_FIXTURE,),
    name="InteraktivWorkingcopyLayer:Integration"
)
INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(INTERAKTIV_WORKINGCOPY_FIXTURE, WSGI_SERVER_FIXTURE),
    name="InteraktivWorkingcopyLayer:Functional"
)
