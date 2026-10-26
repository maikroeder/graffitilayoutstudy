import plone.api as api
from graffiti.pdfcheck.interfaces import IGraffitiPdfcheckLayer, IPdfCheck, IPdfCheckRunner
from graffiti.pdfcheck.settings import available_checks, get_settings
from graffiti.pdfcheck.testing import GRAFFITI_PDFCHECK_INTEGRATION_TESTING
from graffiti.pdfcheck.tests import project_checks
from graffiti.pdfcheck.utilities.local_runner import LocalRunner
from interaktiv.framework.test import TestCase
from plone.browserlayer.utils import registered_layers
from plone.dexterity.fti import DexterityFTI
from zope.component import getGlobalSiteManager, getUtility
from zope.configuration import xmlconfig
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory

# a content type of a project with a file field "file" in its own schema
HANDOUT_MODEL = '''<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="file" type="plone.namedfile.field.NamedBlobFile"><title>File</title></field>
  </schema>
</model>'''


def configlet_ids():
    return [action.getId() for action in api.portal.get_tool('portal_controlpanel').listActions()]


class TestSetup(TestCase):
    layer = GRAFFITI_PDFCHECK_INTEGRATION_TESTING
    product_name = 'graffiti.pdfcheck'

    def test_product_installed(self):
        self.assertTrue(self.is_product_installed(self.product_name))

    def test_browserlayer_registered(self):
        self.assertIn(IGraffitiPdfcheckLayer, registered_layers())

    def test_default_settings(self):
        self.assertEqual(get_settings(), {
            'enabled': True,
            'portal_types': ['File'],
            'checks': ['open', 'text', 'rewrite', 'pdfunite', 'qpdf'],
            'timeout': 30,
            'memory_mb': 1024,
            'max_size_mb': 50,
            'programs': {'pdfunite': 'pdfunite', 'qpdf': 'qpdf'},
        })

    def test_settings_page(self):
        self.assertIn('pdfcheck-settings', configlet_ids())
        alsoProvides(self.request, IGraffitiPdfcheckLayer)
        html = self.portal.restrictedTraverse('@@pdfcheck-settings')()
        self.assertIn('form.widgets.timeout', html)
        self.assertIn('form.widgets.portal_types', html)
        self.assertNotIn('form.widgets.qpdf', html)
        # the built-in checks as check boxes with their titles, names and functions
        self.assertIn('Open the file: damaged, password, edit protection', html)
        self.assertIn('<code>open</code>', html)
        self.assertIn('<code>graffiti.pdfcheck.checks.check_open</code>', html)
        self.assertIn('name="form.widgets.checks:list"', html)
        self.assertIn('name="form.widgets.checks-empty-marker"', html)

    def test_built_in_checks_on_the_settings_page(self):
        vocabulary = getUtility(IVocabularyFactory, 'graffiti.pdfcheck.Checks')(self.portal)
        self.assertEqual([term.value for term in vocabulary], ['open', 'text', 'rewrite', 'pdfunite', 'qpdf'])

    def test_registered_checks_on_the_settings_page(self):
        """ Registered checks follow the built-in checks, with their title """
        xmlconfig.string('''<configure xmlns="http://namespaces.zope.org/zope">
          <include package="zope.component" file="meta.zcml" />
          <utility component="graffiti.pdfcheck.tests.project_checks.ONE_PAGE"
                   provides="graffiti.pdfcheck.interfaces.IPdfCheck" name="one_page" />
        </configure>''')
        self.addCleanup(getGlobalSiteManager().unregisterUtility, project_checks.ONE_PAGE, IPdfCheck, 'one_page')
        vocabulary = getUtility(IVocabularyFactory, 'graffiti.pdfcheck.Checks')(self.portal)
        self.assertEqual([term.value for term in vocabulary],
                         ['open', 'text', 'rewrite', 'pdfunite', 'qpdf', 'one_page'])
        self.assertEqual(vocabulary.getTerm('one_page').title, 'Only one page per file')
        alsoProvides(self.request, IGraffitiPdfcheckLayer)
        html = self.portal.restrictedTraverse('@@pdfcheck-settings')()
        self.assertIn('<code>graffiti.pdfcheck.tests.project_checks.check_one_page</code>', html)
        # not ticked yet: the default settings keep the built-in checks
        self.assertEqual(get_settings()['checks'], ['open', 'text', 'rewrite', 'pdfunite', 'qpdf'])

    def save_settings(self, checks):
        """ The settings page as an editor submits it """
        alsoProvides(self.request, IGraffitiPdfcheckLayer)
        self.request.form.update({
            'form.widgets.enabled': ['selected'], 'form.widgets.enabled-empty-marker': '1',
            'form.widgets.portal_types': ['File'], 'form.widgets.portal_types-empty-marker': '1',
            'form.widgets.checks': checks, 'form.widgets.checks-empty-marker': '1',
            'form.widgets.timeout': '30', 'form.widgets.memory_mb': '1024', 'form.widgets.max_size_mb': '50',
            'form.buttons.save': 'Save',
        })
        return self.portal.restrictedTraverse('@@pdfcheck-settings')()

    def test_save_the_checks(self):
        self.save_settings(['open', 'qpdf'])
        self.assertEqual(get_settings()['checks'], ['open', 'qpdf'])

    def test_save_without_checks(self):
        """ No check box ticked is an error: an empty list would mean all built-in checks """
        api.portal.set_registry_record('graffiti.pdfcheck.checks', ['open'])
        html = self.save_settings([])
        self.assertIn('Choose at least one check.', html)
        self.assertEqual(get_settings()['checks'], ['open'])

    def test_registered_check_with_the_name_of_a_built_in_check(self):
        site_manager = getGlobalSiteManager()
        other = project_checks.ONE_PAGE._replace(name='open')
        site_manager.registerUtility(other, IPdfCheck, 'open')
        self.addCleanup(site_manager.unregisterUtility, other, IPdfCheck, 'open')
        self.assertEqual([check.name for check in available_checks()], ['open', 'text', 'rewrite', 'pdfunite', 'qpdf'])

    def test_content_types_with_a_file_field(self):
        fti = DexterityFTI('Handout', title='Handout', model_source=HANDOUT_MODEL)
        self.portal.portal_types._setObject('Handout', fti)
        vocabulary = getUtility(IVocabularyFactory, 'graffiti.pdfcheck.FileTypes')(self.portal)
        self.assertEqual([term.value for term in vocabulary], ['File', 'Handout'])

    def test_type_whose_schema_can_not_be_loaded(self):
        """ A type of a removed package must not break the settings page """
        fti = DexterityFTI('Removed', title='Removed', schema='graffiti.pdfcheck.tests.removed.IRemoved', model_source='')
        self.portal.portal_types._setObject('Removed', fti)
        vocabulary = getUtility(IVocabularyFactory, 'graffiti.pdfcheck.FileTypes')(self.portal)
        self.assertEqual([term.value for term in vocabulary], ['File'])

    def test_stored_types_that_are_not_offered(self):
        """ Types without a file field, or removed types, stay in the registry and break nothing """
        api.portal.set_registry_record('graffiti.pdfcheck.portal_types', ['File', 'Document', 'Removed'])
        self.assertEqual(get_settings()['portal_types'], ['File', 'Document', 'Removed'])
        alsoProvides(self.request, IGraffitiPdfcheckLayer)
        html = self.portal.restrictedTraverse('@@pdfcheck-settings')()
        self.assertIn('form-widgets-portal_types-0', html)
        self.assertNotIn('value="Document"', html)
        self.assertNotIn('value="Folder"', html)

    def test_runner_utility(self):
        self.assertIsInstance(getUtility(IPdfCheckRunner), LocalRunner)


class TestUninstall(TestCase):
    layer = GRAFFITI_PDFCHECK_INTEGRATION_TESTING
    product_name = 'graffiti.pdfcheck'

    def test_product_uninstalled(self):
        self.uninstall_product(self.product_name)
        self.assertFalse(self.is_product_installed(self.product_name))
        self.assertNotIn(IGraffitiPdfcheckLayer, registered_layers())
        self.assertIsNone(get_settings())
        self.assertNotIn('pdfcheck-settings', configlet_ids())
