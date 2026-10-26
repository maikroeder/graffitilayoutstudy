# -*- coding: utf-8 -*-
import unittest

import plone.api as api
import transaction
from interaktiv.framework import locking
from interaktiv.workingcopy.testing import \
    INTERAKTIV_WORKINGCOPY_FUNCTIONAL_TESTING
from interaktiv.workingcopy.utilities import workingcopy as workingcopy_utility
from plone.app.iterate.dexterity.relation import StagingRelationValue
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.locking.interfaces import STEALABLE_LOCK
from plone.portlets.interfaces import IPortletType
from plone.protect.utils import addTokenToUrl
from plone.testing.zope import Browser
from zope.component import getUtility


class TestWorkingcopyUtility(unittest.TestCase):
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
        self.document = createContentInContainer(self.portal, 'Document', id='document')
        transaction.commit()

    def setup_browser(self, name, password):
        browser = Browser(self.app)
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (name, password,))
        return browser

    @staticmethod
    def _create_workingcopy(obj):
        obj_request = obj.REQUEST
        obj_request.form['form.button.Checkout'] = ''
        checkout_view = api.content.get_view(
            name='arbeitskopie-erstellen',
            context=obj,
            request=obj_request
        )
        checkout_view()
        return True

    def test_workingcopy_utility_get_relations(self):
        original = self.portal['document']
        relations = workingcopy_utility.get_relations(original)
        self.assertEqual(len(relations), 0)

        self._create_workingcopy(original)
        relations = workingcopy_utility.get_relations(original)
        self.assertEqual(len(relations), 1)

    def test_workingcopy_utility_get_relations_portlets_are_addable(self):
        """ Note: This is some weirdo test. Dont ask why, but is was a problem to add portlets"""
        # setup: prepare test browser
        browser = self.setup_browser(name=TEST_USER_NAME, password=TEST_USER_PASSWORD)

        # setup: Make sure there is at least one portlet
        portlet = getUtility(IPortletType, name='plone.portlet.static.Static')
        mapping = self.document.restrictedTraverse(
            '++contextportlets++plone.leftcolumn'
        )
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(
            data={'header': u"test title 1", 'text': u"test text 1"}
        )

        transaction.commit()

        # do it: add second portlet via browser
        portlet_addform_url = f'{mapping.absolute_url()}/+/{portlet.addview}'
        browser.open(addTokenToUrl(portlet_addform_url))

    def test_workingcopy_utility_get_checkout_relation(self):
        original = self.portal['document']
        relation = workingcopy_utility.get_checkout_relation(original)
        self.assertFalse(relation)

        self._create_workingcopy(original)
        relation = workingcopy_utility.get_checkout_relation(original)
        self.assertIsInstance(relation, StagingRelationValue)

    def test_workingcopy_utility_get_original(self):
        original = self.portal['document']
        original_via_util = workingcopy_utility.get_original(original)
        self.assertFalse(original_via_util)

        self._create_workingcopy(original)
        working_copy = self.portal['copy_of_document']

        original_via_util = workingcopy_utility.get_original(original)
        self.assertEqual(original, original_via_util)
        self.assertNotEqual(working_copy, original_via_util)

        original_via_util = workingcopy_utility.get_original(working_copy)
        self.assertEqual(original, original_via_util)
        self.assertNotEqual(working_copy, original_via_util)

    def test_workingcopy_utility_get_working_copy(self):
        original = self.portal['document']
        working_copy_via_util = workingcopy_utility.get_working_copy(original)
        self.assertFalse(working_copy_via_util)

        self._create_workingcopy(original)
        working_copy = self.portal['copy_of_document']

        working_copy_via_util = workingcopy_utility.get_working_copy(original)
        self.assertNotEqual(original, working_copy_via_util)
        self.assertEqual(working_copy, working_copy_via_util)

        working_copy_via_util = workingcopy_utility.get_working_copy(
            working_copy
        )
        self.assertNotEqual(original, working_copy_via_util)
        self.assertEqual(working_copy, working_copy_via_util)

    def tearDown(self):
        if 'document' in self.portal.objectIds():
            locking.force_unlock(self.portal['document'], STEALABLE_LOCK)
            self.portal.manage_delObjects(['document'])
        if 'copy_of_document' in self.portal.objectIds():
            self.portal.manage_delObjects(['copy_of_document'])
        transaction.commit()
