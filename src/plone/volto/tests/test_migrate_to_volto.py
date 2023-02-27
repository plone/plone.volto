from Acquisition import aq_base
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.volto.content import FolderishDocument
from plone.volto.content import FolderishEvent
from plone.volto.content import FolderishNewsItem
from plone.volto.testing import PLONE_6
from plone.volto.testing import PLONE_VOLTO_MIGRATION_FUNCTIONAL_TESTING
from Products.CMFPlone.utils import get_installer

import json
import responses
import unittest


@unittest.skipIf(
    not PLONE_6,
    "This test is only intended to run for Plone 6",
)
class TestMigrateToVolto(unittest.TestCase):

    layer = PLONE_VOLTO_MIGRATION_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal_url = self.portal.absolute_url()

    def test_form_renders(self):
        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        html = view()
        self.assertIn("Migrate to Volto", html)

    def test_plonevolto_is_installed(self):
        installer = get_installer(self.portal, self.request)
        self.assertFalse(installer.is_product_installed("plone.volto"))

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        self.assertTrue(installer.is_product_installed("plone.volto"))

    def test_items_are_migrated_to_folderish(self):
        doc = api.content.create(
            container=self.portal,
            type="Document",
            id="doc",
            title="Document",
        )
        news = api.content.create(
            container=self.portal,
            type="News Item",
            id="news",
            title="News Item",
        )
        doc = api.content.create(
            container=self.portal,
            type="Event",
            id="event",
            title="Event",
        )

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        doc = self.portal["doc"]
        self.assertEqual(doc.portal_type, "Document")
        self.assertTrue(aq_base(doc).isPrincipiaFolderish)
        self.assertEqual(doc.__class__, FolderishDocument)

        news = self.portal["news"]
        self.assertEqual(news.portal_type, "News Item")
        self.assertTrue(aq_base(news).isPrincipiaFolderish)
        self.assertEqual(news.__class__, FolderishNewsItem)

        event = self.portal["event"]
        self.assertEqual(event.portal_type, "Event")
        self.assertTrue(aq_base(event).isPrincipiaFolderish)
        self.assertEqual(event.__class__, FolderishEvent)

        # Test that doc renders without error.
        doc.__call__()
        # We can add content
        news_in_doc = api.content.create(
            container=doc,
            type="News Item",
            id="news-in-doc",
            title="News in Doc",
        )
        self.assertEqual(news_in_doc.__class__, FolderishNewsItem)

    def test_folders_are_migrated(self):
        api.content.create(
            container=self.portal,
            type="Folder",
            id="folder1",
            title="Folder 1",
        )
        self.assertEqual(self.portal["folder1"].portal_type, "Folder")

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        doc = self.portal["folder1"]
        self.assertEqual(doc.portal_type, "Document")
        self.assertTrue(aq_base(doc).isPrincipiaFolderish)
        self.assertEqual(doc.__class__, FolderishDocument)

    def test_collections_are_migrated(self):
        collection = api.content.create(
            container=self.portal,
            type="Collection",
            id="collection",
            title="Collection",
        )
        collection.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["Document"],
            }
        ]
        collection.sort_on = "effective"
        collection.sort_reversed = False
        collection.limit = 100
        collection.item_count = 10
        self.assertEqual(self.portal["collection"].portal_type, "Collection")

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        collection = self.portal["collection"]
        self.assertEqual(collection.portal_type, "Document")
        aq_base(collection).isPrincipiaFolderish
        self.assertTrue(aq_base(collection).isPrincipiaFolderish)
        self.assertEqual(collection.__class__, FolderishDocument)

        listing = collection.blocks[collection.blocks_layout["items"][1]]
        self.assertEqual(listing["@type"], "listing")
        self.assertEqual(
            listing["querystring"],
            {
                "b_size": 10,
                "limit": 100,
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"],
                    }
                ],
                "sort_on": "effective",
                "sort_order_boolean": False,
                "sort_order": "ascending",
            },
        )

    def test_default_pages_are_migrated(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="folder",
            title="Folder",
        )
        api.content.create(
            container=folder,
            type="Document",
            id="doc",
            title="Document",
            description="This is a default page",
        )
        folder.setDefaultPage("doc")

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        folder = self.portal["folder"]
        self.assertEqual(folder.portal_type, "Document")
        self.assertIsNone(getattr(folder, "default_page", None))
        self.assertEqual(folder.title, "Document")
        self.assertEqual(folder.description, "This is a default page")

    def test_default_page_collections_are_migrated(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="folder",
            title="Folder",
        )
        collection = api.content.create(
            container=folder,
            type="Collection",
            id="collection",
            title="Collection",
            description="This is a default collection",
            limit=1000,
            item_count=30,
            sort_on="modified",
            sort_reversed=True,
        )
        collection.query = [
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.relativePath",
                "v": "..::1",
            },
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.any",
                "v": ["Document"],
            },
        ]
        folder.setDefaultPage("collection")
        api.content.create(
            container=folder,
            type="Document",
            id="doc1",
            title="Doc 1",
            description="This is a document",
        )
        api.content.create(
            container=folder,
            type="Document",
            id="doc2",
            title="Doc 2",
            description="This is a document",
        )
        self.assertIn("collection", folder.keys())
        self.assertEqual(len(collection.results()), 2)

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        folder = self.portal["folder"]
        self.assertEqual(folder.portal_type, "Document")
        self.assertIsNone(getattr(folder, "default_page", None))
        self.assertNotIn("collection", folder.keys())
        self.assertEqual(folder.title, "Collection")
        self.assertEqual(folder.description, "This is a default collection")
        listing = collection.blocks[collection.blocks_layout["items"][1]]
        self.assertEqual(listing["@type"], "listing")
        self.assertEqual(
            listing["querystring"],
            {
                "b_size": 30,
                "limit": 1000,
                "query": [
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.relativePath",
                        "v": ".::1",
                    },
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["Document"],
                    },
                ],
                "sort_on": "modified",
                "sort_order_boolean": True,
                "sort_order": "descending",
            },
        )

    def test_default_page_news_are_not_migrated(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            id="folder",
            title="Folder",
            description="This of the folder",
        )
        api.content.create(
            container=folder,
            type="News Item",
            id="news",
            title="News Item",
            description="This is a default news item",
        )
        folder.setDefaultPage("news")
        self.assertIn("news", folder.keys())

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        view()

        folder = self.portal["folder"]
        self.assertEqual(folder.portal_type, "Document")
        # the default_page attr is not removed
        self.assertEqual(folder.default_page, "news")
        self.assertEqual(folder.title, "Folder")
        self.assertEqual(folder.description, "This of the folder")

        self.assertIn("news", folder.keys())
        self.assertEqual(folder["news"].portal_type, "News Item")
        self.assertEqual(folder["news"].title, "News Item")
        self.assertEqual(folder["news"].description, "This is a default news item")

    @responses.activate
    def test_richtext_is_migrated(self):
        # Mock response of blocks-conversion-tool for slate
        html = "<p>I am <a href='https://www.plone.org'>html</a> text</p>"
        result = json.loads(
            """{"data":[{"@type":"slate","value":[{"type":"p","children":[{"text":"I am "},{"type":"link","data":{"url":"https://www.plone.org","title":null,"target":null},"children":[{"text":"html"}]},{"text":" text"}]}],"plaintext":"I am html text"}]}"""
        )
        responses.add(
            responses.POST,
            url="http://localhost:5000/html",
            json=result,
        )

        doc = api.content.create(
            container=self.portal,
            type="Document",
            id="doc",
            title="Document",
            text=RichTextValue(html, "text/plain", "text/html"),
        )
        self.assertTrue(isinstance(doc.text, RichTextValue))

        view = self.portal.restrictedTraverse("@@migrate_to_volto")
        self.request.form["form.submitted"] = True
        self.request.form["slate"] = True
        view()

        doc = self.portal["doc"]
        self.assertIsNone(doc.text)
        uuid = doc.blocks_layout["items"][1]
        block = doc.blocks[uuid]
        self.assertEqual(block["plaintext"], "I am html text")
