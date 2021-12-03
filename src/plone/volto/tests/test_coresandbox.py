# -*- coding: utf-8 -*-
from plone.volto.testing import PLONE_VOLTO_CORESANDBOX_FUNCTIONAL_TESTING

# from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import RelativeSession

# import transaction
import unittest


class TestCoresandbox(unittest.TestCase):

    layer = PLONE_VOLTO_CORESANDBOX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_coresandbox_example_content_schema_endpoint(self):
        response = self.api_session.get("/@types/example")

        self.assertEqual(response.status_code, 200)
