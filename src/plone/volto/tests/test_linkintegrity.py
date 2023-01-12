# -*- coding: utf-8 -*-
from plone.app.linkintegrity.interfaces import IRetriever
from plone.uuid.interfaces import IUUID
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING
from unittest import TestCase


class TestBlocksLinkintegrity(TestCase):
    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "Document", id="doc1", title="Document with Blocks"
            )
        ]
        self.doc2 = self.portal[
            self.portal.invokeFactory("Document", id="doc2", title="Target Document")
        ]

    def retrieve_links(self, value):
        retriever = IRetriever(self.portal.doc1)
        return retriever.retrieveLinks()

    def test_links_retriever_return_internal_links_in_nested_columns(self):
        uid = IUUID(self.doc2)
        blocks = {
            "111": {
                "@type": "__grid",
                "columns": [
                    {
                        "@type": "teaser",
                        "href": f"../resolveuid/{uid}",
                    }
                ],
            },
        }
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn(f"../resolveuid/{uid}", value)

    def test_links_retriever_return_internal_links_in_nested_hrefList(self):
        uid = IUUID(self.doc2)
        blocks = {
            "111": {
                "hrefList": [
                    {
                        "href": f"../resolveuid/{uid}",
                    }
                ],
            },
        }
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn(f"../resolveuid/{uid}", value)

    def test_links_retriever_return_internal_links_in_nested_slides(self):
        uid = IUUID(self.doc2)
        blocks = {
            "111": {
                "slides": [
                    {
                        "href": f"../resolveuid/{uid}",
                    }
                ],
            },
        }
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn(f"../resolveuid/{uid}", value)
