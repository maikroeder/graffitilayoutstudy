# -*- coding: utf-8 -*-
from interaktiv.framework.test import TestCase
from Products.CMFCore.utils import getToolByName
from interaktiv.workingcopy.testing import \
    INTERAKTIV_WORKINGCOPY_INTEGRATION_TESTING


class TestSetup(TestCase):
    layer = INTERAKTIV_WORKINGCOPY_INTEGRATION_TESTING
    product_name = 'interaktiv.workingcopy'

    def setUp(self):
        super(TestSetup, self).setUp()

    def test_product_installed(self):
        installer = self.get_installer()
        self.assertTrue(installer.is_product_installed(self.product_name))

    def test_workingcopy_user_action_added(self):
        portal_actions = getToolByName(self.portal, 'portal_actions')
        action_ids = [action.id for action in portal_actions.listActions()]
        expected_actions_ids = [
            'workingcopy_checkin',
            'workingcopy_checkout',
            'workingcopy_checkout_cancel'
        ]
        for expected_action_id in expected_actions_ids:
            self.assertTrue(expected_action_id in action_ids)
