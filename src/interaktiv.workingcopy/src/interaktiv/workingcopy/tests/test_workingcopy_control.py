# -*- coding: utf-8 -*-
import plone.api as api
import transaction
import unittest2 as unittest
from interaktiv.framework import locking
from interaktiv.workingcopy.testing import \
    INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer


class TestWorkingcopyControl(unittest.TestCase):
    layer = INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
    app = None
    portal = None
    request = None
    document = None

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        createContentInContainer(self.portal, 'Document', id='document')
        transaction.commit()

    def _create_workingcopy(self, obj):
        obj_id = obj.id
        obj_request = obj.REQUEST
        obj_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=obj,
            request=obj_request
        )
        checkout_view()
        self.assertTrue(obj_id in self.portal)
        return True

    def _checkin_workingcopy(self, obj):
        obj_id = obj.id
        obj_request = obj.REQUEST
        obj_request.form['form.button.Checkin'] = ''
        checkin_view = api.content.get_view(
            name='arbeitskopie-mit-original-austauschen',
            context=obj,
            request=obj_request
        )
        checkin_view()
        self.assertFalse(obj_id in self.portal)
        return True

    def test_workingcopy_control_checkout_allowed(self):
        # 1. check if original can checkout
        original = self.portal['document']
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertTrue(control_view.checkout_allowed())

        # 2. check if original can checkout after creating a working copy
        self._create_workingcopy(original)
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertFalse(control_view.checkout_allowed())

        # 3. check if working copy can checkout
        working_copy = self.portal['copy_of_document']
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=working_copy,
            request=working_copy.REQUEST
        )
        self.assertFalse(control_view.checkout_allowed())

        # 4. check if original can checkout after checkin
        self._checkin_workingcopy(working_copy)
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertTrue(control_view.checkout_allowed())

    def test_workingcopy_control_checkin_allowed(self):
        # 1. check if original can checkin
        original = self.portal['document']
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertFalse(control_view.checkin_allowed())

        # 3. check if working copy can checkin
        self._create_workingcopy(original)
        working_copy = self.portal['copy_of_document']
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=working_copy,
            request=working_copy.REQUEST
        )
        self.assertTrue(control_view.checkin_allowed())

        # 4. check if original can checkin after checkin
        self._checkin_workingcopy(working_copy)
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertFalse(control_view.checkin_allowed())

    def test_workingcopy_control_cancel_allowed(self):
        # 1. check if original can cancel
        original = self.portal['document']
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertFalse(control_view.cancel_allowed())

        # 2. check if original can cancel after creating a working copy
        self._create_workingcopy(original)
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertFalse(control_view.cancel_allowed())

        # 3. check if working copy can cancel
        working_copy = self.portal['copy_of_document']
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=working_copy,
            request=working_copy.REQUEST
        )
        self.assertTrue(control_view.cancel_allowed())

        # 4. check if original can checkout after checkin
        self._checkin_workingcopy(working_copy)
        control_view = api.content.get_view(
            name='workingcopy_control',
            context=original,
            request=original.REQUEST
        )
        self.assertFalse(control_view.cancel_allowed())

    def tearDown(self):
        if 'document' in self.portal.objectIds():
            locking.clear_locks(self.portal['document'])
            self.portal.manage_delObjects(['document'])
        if 'copy_of_document' in self.portal.objectIds():
            self.portal.manage_delObjects(['copy_of_document'])
        transaction.commit()
