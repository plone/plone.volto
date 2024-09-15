# -*- coding: utf-8 -*-
import unittest

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles
from plone.stringinterp.interfaces import IStringInterpolator

from plone.volto.interpolators.volto_portal_url import (
    VoltoPortalURLSubstitution,
)
from plone.volto.interpolators.volto_absolute_url import (
    VoltoAbsoluteURLSubstitution,
)
from plone.volto.testing import (
    PLONE_VOLTO_CORE_INTEGRATION_TESTING,
    PLONE_VOLTO_CORE_FUNCTIONAL_TESTING,
)


class TestSubstitutions(unittest.TestCase):
    """Test case for substitutions"""

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_volto_portal_url(self):
        """test for volto_portal_url"""
        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        substitution = VoltoPortalURLSubstitution(self.portal)()
        self.assertEqual(substitution, volto_url)

    def test_string_interpolation_volto_portal_url(self):
        """test interpolating as string"""
        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        string = "${volto_portal_url}"
        value = IStringInterpolator(self.portal)(string)
        self.assertEqual(value, volto_url)


class TestSubstitutionsFunctional(unittest.TestCase):
    """Test case for substitutions"""

    layer = PLONE_VOLTO_CORE_FUNCTIONAL_TESTING

    def setUp(self):
        """test setup"""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.portal.invokeFactory("Document", id="doc", title="My Document")
        self.document = self.portal.get("doc")

    def test_volto_absolute_url(self):
        """test for volto_absolute_url"""

        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        portal_url = self.portal.absolute_url()
        context_url = self.document.absolute_url()
        substitution = VoltoAbsoluteURLSubstitution(self.document)()
        self.assertEqual(substitution, context_url.replace(portal_url, volto_url))

    def test_string_interpolation_volto_absolute_url(self):
        """test as string interpolator"""

        volto_url = api.portal.get_registry_record("volto.frontend_domain")
        portal_url = self.portal.absolute_url()
        context_url = self.document.absolute_url()

        string = "${volto_absolute_url}"
        value = IStringInterpolator(self.document)(string)
        self.assertEqual(value, context_url.replace(portal_url, volto_url))
