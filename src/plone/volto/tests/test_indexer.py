# -*- coding: utf-8 -*-
""" test indexer module """
# pylint: disable=import-error,no-name-in-module,too-few-public-methods,
# pylint: disable=not-callable,no-self-use,unused-argument,invalid-name
import unittest

from zope.component import queryUtility
import transaction
from eea.volto.slate.tests.base import FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer


class TestSearchTextInBlocks(unittest.TestCase):
    """TestSearchTextInBlocks."""

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = list(fti.behaviors)
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.doc = createContentInContainer(
            self.portal, u"Document", id=u"doc", title=u"A document"
        )
        transaction.commit()

    def test_search_text(self):
        """test_search_text."""
        self.doc.blocks = {
            "38541872-06c2-41c9-8709-37107e597b18": {
                "@type": "slate",
                "plaintext": "Under a new climatic regime, therefore",
                "value": [],
            },
            "4fcfeb9b-f73e-427c-9e06-2e4d53b06865": {
                "@type": "slate",
                "searchableText": "EEA Climate Change data centre",
                "value": [],
            },
        }
        self.doc.blocks_layout = [
            "38541872-06c2-41c9-8709-37107e597b18",
            "4fcfeb9b-f73e-427c-9e06-2e4d53b06865",
        ]
        self.portal.portal_catalog.indexObject(self.doc)

        query = {"SearchableText": "climatic"}
        results = self.portal.portal_catalog.searchResults(**query)
        self.assertEqual(len(results), 1)

        brain = results[0]
        self.assertEqual(brain.Title, "A document")

        query = {"SearchableText": "EEA"}
        results = self.portal.portal_catalog.searchResults(**query)
        self.assertEqual(len(results), 1)

        brain = results[0]
        self.assertEqual(brain.Title, "A document")
