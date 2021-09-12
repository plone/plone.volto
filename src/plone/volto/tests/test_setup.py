# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING  # noqa
from plone import api

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:  # Plone < 5.1
    HAS_INSTALLER = False
else:
    HAS_INSTALLER = True

import unittest


class TestSetup(unittest.TestCase):
    """Test that plone.volto is properly installed."""

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if HAS_INSTALLER:
            self.installer = get_installer(self.portal)
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if plone.volto is installed."""
        if HAS_INSTALLER:
            self.assertTrue(self.installer.is_product_installed("plone.volto"))
        else:
            self.assertTrue(self.installer.isProductInstalled("plone.volto"))

    def test_browserlayer(self):
        """Test that IPloneVoltoCoreLayer is registered."""
        from plone.volto.interfaces import IPloneVoltoCoreLayer
        from plone.browserlayer import utils

        self.assertIn(IPloneVoltoCoreLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if HAS_INSTALLER:
            self.installer = get_installer(self.portal)
            self.installer.uninstall_product("plone.volto")
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
            self.installer.uninstallProducts(["plone.volto"])

    def test_product_uninstalled(self):
        """Test if plone.volto is cleanly uninstalled."""
        if HAS_INSTALLER:
            self.assertFalse(self.installer.is_product_installed("plone.volto"))
        else:
            self.assertFalse(self.installer.isProductInstalled("plone.volto"))

    def test_browserlayer_removed(self):
        """Test that IPloneVoltoCoreLayer is removed."""
        from plone.volto.interfaces import IPloneVoltoCoreLayer
        from plone.browserlayer import utils

        self.assertNotIn(IPloneVoltoCoreLayer, utils.registered_layers())
