import interaktiv.framework as framework
import plone.api as api
import transaction
from Acquisition import aq_base
from DateTime import DateTime
from interaktiv.framework import locking
from interaktiv.framework.test import TestCase
from interaktiv.workingcopy.testing import INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
from interaktiv.workingcopy.viewlets.info import InteraktivInfoWorkingcopyViewlet
from plone.app.testing import TEST_USER_ID
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestWorkingcopy(TestCase):
    layer = INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
    document = None

    def setUp(self):
        super(TestWorkingcopy, self).setUp()
        self.document = api.content.create(
            container=self.portal,
            type='Document',
            id='document',
            title="Document",
            description='Document Description'
        )

    def tearDown(self):
        locking.clear_locks(self.document)
        self.delete(self.portal, self.document.id)

    def _get_checkout_info(self, workingcopy):
        info_viewlet = InteraktivInfoWorkingcopyViewlet(
            workingcopy, self.request, None, None
        )
        return {
            'created': info_viewlet.created(),
            'creator': info_viewlet.creator()
        }

    def test_workingcopy_checkout_and_checkin(self):
        # setup: get original
        original = self.portal['document']
        original_request = original.REQUEST

        # do it: checkout original
        original_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()

        # postcondition: workingcopy created
        workingcopy = self.portal['copy_of_document']
        workingcopy_request = workingcopy.REQUEST
        self.assertTrue(workingcopy)

        # do it: checkin workingcopy
        workingcopy_request.form['form.button.Checkin'] = ''
        checkin_view = api.content.get_view(
            name='arbeitskopie-mit-original-austauschen',
            context=workingcopy,
            request=workingcopy_request
        )
        checkin_view.workingcopy_workflow_name = ''
        checkin_view()

        # postcondition: workingcopy checked in
        self.assertTrue('document' in self.portal)
        self.assertTrue('copy_of_document' not in self.portal)

    def test_workingcopy_checkout_and_checkin_with_field_changes(self):
        # setup: get original
        original = self.portal['document']
        original_request = original.REQUEST

        # do it: checkout original
        original_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()

        # postcondition: original still same
        workingcopy = self.portal['copy_of_document']
        workingcopy_request = workingcopy.REQUEST
        self.assertEqual(original.title, 'Document')
        self.assertEqual(original.title, workingcopy.title)
        self.assertEqual(original.description, 'Document Description')
        self.assertEqual(original.description, workingcopy.description)

        # setup: change title and description of workingcopy
        setattr(workingcopy, 'title', 'Document NEW')
        setattr(workingcopy, 'description', 'Document Description NEW')

        # do it: checkin workingcopy to set this changes
        workingcopy_request.form['form.button.Checkin'] = ''
        checkin_view = api.content.get_view(
            name='arbeitskopie-mit-original-austauschen',
            context=workingcopy,
            request=workingcopy_request
        )
        checkin_view.workingcopy_workflow_name = ''
        checkin_view()

        # postcondition: new changes are now in original
        self.assertEqual(original.Title(), 'Document NEW')
        self.assertEqual(original.Description(), 'Document Description NEW')

        # postcondition: workingcopy checked in
        self.assertTrue('document' in self.portal)
        self.assertTrue('copy_of_document' not in self.portal)

    def test_workingcopy_checkout_and_checkin_history(self):
        # setup: get original
        original = self.portal['document']
        original_request = original.REQUEST

        # do it: checkout original
        original_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()

        # postcondition: original still same
        workingcopy = self.portal['copy_of_document']
        workingcopy_request = workingcopy.REQUEST
        self.assertEqual(original.title, 'Document')
        self.assertEqual(original.title, workingcopy.title)
        self.assertEqual(original.description, 'Document Description')
        self.assertEqual(original.description, workingcopy.description)

        # do it: checkin workingcopy
        workingcopy_request.form['form.button.Checkin'] = ''
        checkin_view = api.content.get_view(
            name='arbeitskopie-mit-original-austauschen',
            context=workingcopy,
            request=workingcopy_request
        )
        checkin_view.workingcopy_workflow_name = ''
        checkin_view()

        # postcondition: check history
        original_full_history = framework.history.get_full_history(original)
        self.assertTrue(len(original_full_history), 3)

    def test_workingcopy_checkout_and_cancel(self):
        original = self.portal['document']
        original_request = original.REQUEST

        # 1. Checkout Original
        original_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()
        workingcopy = self.portal['copy_of_document']
        workingcopy_request = workingcopy.REQUEST
        self.assertTrue(workingcopy)

        # 2. Change Title of Workingcopy
        setattr(workingcopy, 'title', 'Document NEW')

        # 3. Cancel Workingcopy
        workingcopy_request.form['form.button.Cancel'] = ''
        cancel_view = api.content.get_view(
            name='arbeitskopie-verwerfen',
            context=workingcopy,
            request=workingcopy_request
        )
        cancel_view()
        self.assertTrue('document' in self.portal)
        self.assertTrue('copy_of_document' not in self.portal)
        self.assertEqual(original.title, 'Document')

    def test_workingcopy_checkout_sets_version_notice(self):
        original = self.portal['document']
        original_request = original.REQUEST

        original_request.form['form.button.Checkout'] = ''
        original_request.form['version_notice'] = 'a wcopy notice'
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()
        workingcopy = self.portal['copy_of_document']
        self.assertEqual(
            workingcopy.working_copy_version_notice,
            'a wcopy notice'
        )

        # teardown
        self.delete(self.portal, 'copy_of_document')

    def test_workingcopy_checkout_sets_checkout_info(self):
        original = self.portal['document']
        original_request = original.REQUEST

        original_request.form['form.button.Checkout'] = ''
        original_request.form['version_notice'] = 'a wcopy notice'
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=original_request
        )
        checkout_view()
        workingcopy = self.portal['copy_of_document']

        checkout_info = self._get_checkout_info(workingcopy)
        self.assertEqual(checkout_info['creator'].id, TEST_USER_ID)

        today = DateTime()
        translation_utility = api.portal.get_tool('translation_service')
        expected_created = translation_utility.ulocalized_time(today, context=workingcopy, domain='plonelocales')
        self.assertEqual(checkout_info['created'], expected_created)

        # teardown
        self.delete(self.portal, 'copy_of_document')

    def test_workingcopy_deleting_workingcopy_removes_relation(self):
        # setup: get original
        original = self.portal['document']

        # setup: create workingcopy
        self.request.form = {'form.button.Checkout': ''}
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=self.request
        )
        checkout_view()

        # do it: delete workingcopy by hand
        self.portal.manage_delObjects(['copy_of_document'])
        transaction.commit()

        # postcondition: check if not in relation catalog anymore
        intids = getUtility(IIntIds)
        catalog = getUtility(ICatalog)
        original_from_id = intids.queryId(aq_base(original))
        relations = list(catalog.findRelations({'from_id': original_from_id}))
        self.assertEqual(len(relations), 0)
