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
from plone.locking.interfaces import STEALABLE_LOCK


class TestWorkingcopyLocking(unittest.TestCase):
    layer = INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
    app = None
    portal = None
    request = None

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        createContentInContainer(
            self.portal,
            'Document',
            id='document',
            title="Document",
            description='Document Description'
        )
        transaction.commit()

    def test_workingcopy_locking_checkout_locks_original(self):
        original = self.portal['document']
        self.request.form = {
            'form.button.Checkout': ''
        }
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=self.request
        )
        checkout_view()
        #
        self.assertTrue(locking.is_locked(original))
        #
        locking.unlock(original, STEALABLE_LOCK)

    def test_workingcopy_locking_checkin_yields_unlocked(self):
        original = self.portal['document']
        self.assertFalse(locking.is_locked(original))

        # 1. create workingcopy
        self.request.form = {'form.button.Checkout': ''}
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=self.request
        )
        checkout_view()
        workingcopy = self.portal['copy_of_document']
        self.assertTrue(locking.is_locked(original))
        self.assertFalse(locking.is_locked(workingcopy))

        # 2. checkin changed workingcopy
        workingcopy.title = 'Document edited via WC'
        self.request.form = {'form.button.Checkin': ''}
        checkin_view = api.content.get_view(
            name='arbeitskopie-mit-original-austauschen',
            context=workingcopy,
            request=self.request
        )
        checkin_view()
        new_original = self.portal['document']

        # check if its replaced
        self.assertEqual(new_original.title, 'Document edited via WC')
        self.assertFalse(locking.is_locked(new_original))

    def test_workingcopy_locking_deleting_workingcopy_unlocks_original(self):
        original = self.portal['document']
        self.assertFalse(locking.is_locked(original))

        self.request.form = {
            'form.button.Checkout': ''
        }
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=original,
            request=self.request
        )
        checkout_view()
        self.assertTrue(locking.is_locked(original))

        self.portal.manage_delObjects(['copy_of_document'])
        self.assertFalse(locking.is_locked(original))

    def tearDown(self):
        if 'copy_of_document' in self.portal.objectIds():
            self.portal.manage_delObjects(['copy_of_document'])
        if 'document' in self.portal.objectIds():
            locking.clear_locks(self.portal['document'])
            self.portal.manage_delObjects(['document'])
        transaction.commit()
