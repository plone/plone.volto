# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from importlib import import_module
from plone import api
from plone.volto.bbb import get_installer
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING  # noqa

import unittest


PLONE_6 = getattr(import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False)


class TestSetup(unittest.TestCase):
    """Test that plone.volto is properly installed."""

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if plone.volto is installed."""
        self.assertTrue(self.installer.is_product_installed("plone.volto"))

    def test_browserlayer(self):
        """Test that IPloneVoltoCoreLayer is registered."""
        from plone.browserlayer import utils
        from plone.volto.interfaces import IPloneVoltoCoreLayer

        self.assertIn(IPloneVoltoCoreLayer, utils.registered_layers())

    @unittest.skipIf(
        not PLONE_6,
        "This test is only intended to run for Plone 6",
    )
    def test_plone_site_has_blocks_behavior(self):
        pt = api.portal.get_tool("portal_types")
        fti = pt.getTypeInfo("Plone Site")

        self.assertTrue("volto.blocks" in fti.behaviors)

    def test_plone_site_has_edit_action_setup(self):
        pt = api.portal.get_tool("portal_types")
        fti = pt.getTypeInfo("Plone Site")

        action_obj = fti.getActionObject("object/edit")
        self.assertIsNotNone(action_obj)
        self.assertTrue("Modify portal content" in action_obj.permissions)


class TestUninstall(unittest.TestCase):

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)
        self.installer.uninstall_product("plone.volto")

    def test_product_uninstalled(self):
        """Test if plone.volto is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("plone.volto"))

    def test_browserlayer_removed(self):
        """Test that IPloneVoltoCoreLayer is removed."""
        from plone.browserlayer import utils
        from plone.volto.interfaces import IPloneVoltoCoreLayer

        self.assertNotIn(IPloneVoltoCoreLayer, utils.registered_layers())
