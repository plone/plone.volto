# -*- coding: utf-8 -*-
from plone.uuid.interfaces import IUUID
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING  # noqa
from plone.app.querystring.queryparser import Row
from plone.volto.queryparser import _objectbrowserReference

import unittest


class TestQueryparser(unittest.TestCase):

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory("Document", id="doc1")

    def test_objectbrowser_reference_operator(self):
        doc_uid = IUUID(self.portal.doc1)
        values = {
            "object": {"UID": doc_uid},
        }
        data = Row(
            index="path",
            operator="plone.app.querystring.operation.string.objectBrowserReference",
            values=values,
        )
        parsed = _objectbrowserReference(self.portal, data)
        expected = {"path": {"query": ["/".join(self.portal.doc1.getPhysicalPath())]}}
        self.assertEqual(parsed, expected)

    def test_objectbrowser_reference_operator_accept_depth(self):
        doc_uid = IUUID(self.portal.doc1)
        values = {"object": {"UID": doc_uid}, "depth": 1}
        data = Row(
            index="path",
            operator="plone.app.querystring.operation.string.objectBrowserReference",
            values=values,
        )
        parsed = _objectbrowserReference(self.portal, data)
        expected = {
            "path": {
                "query": ["/".join(self.portal.doc1.getPhysicalPath())],
                "depth": 1,
            }
        }
        self.assertEqual(parsed, expected)
