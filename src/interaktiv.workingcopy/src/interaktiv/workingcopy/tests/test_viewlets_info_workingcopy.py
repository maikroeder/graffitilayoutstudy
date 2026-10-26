import interaktiv.framework as framework
import plone.api as api
from interaktiv.framework import locking
from interaktiv.framework.test import TestCase
from interaktiv.workingcopy.testing import INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
from interaktiv.workingcopy.viewlets.info import InteraktivInfoWorkingcopyViewlet


class TestInteraktivInfoWorkingcopyViewlet(TestCase):
    layer = INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
    document = None

    def setUp(self):
        super(TestInteraktivInfoWorkingcopyViewlet, self).setUp()
        self.document = api.content.create(
            container=self.portal,
            type='Document',
            id='document',
            title="Document",
            description='Document Description'
        )
        framework.workflow.set_review_state(self.document, 'publish')
        self.assertTrue(framework.workflow.is_review_state(self.document, 'published'))

        # setup
        original = self.portal['document']
        original_request = original.REQUEST
        original_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()

        # postcondition: workingcopy created
        self.workingcopy = self.portal['copy_of_document']
        self.viewlet: InteraktivInfoWorkingcopyViewlet = framework.helper.get_viewlet(
            context=self.workingcopy,
            request=self.workingcopy.REQUEST,
            viewlet_name='interaktiv.workingcopy.info_workingcopy',
            viewlet_manager_name='plone.abovecontent'
        )

    def tearDown(self):
        locking.clear_locks(self.document)
        self.delete(self.portal, self.document.id)

    def test_is_original(self):
        self.assertFalse(self.viewlet.is_original())

    def test_original(self):
        # do it
        result = self.viewlet.original()

        # postcondition
        self.assertEqual(result.UID(), self.document.UID())

    def test__getReference(self):
        # do it
        result = self.viewlet._getReference()

        # postcondition
        self.assertEqual(result.UID(), self.document.UID())

    def test_created(self):
        # do it
        result = self.viewlet.created()

        # postcondition
        self.assertIsInstance(result, str)
        self.assertTrue(result)

    def test_creator(self):
        # do it
        result = self.viewlet.creator()

        # postcondition
        self.assertEqual(result.id, self.workingcopy.Creator())
