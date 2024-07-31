from Acquisition import aq_base
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.volto.content import FolderishDocument
from plone.volto.content import FolderishEvent
from plone.volto.content import FolderishNewsItem

import json
import pytest
import responses


@pytest.fixture
def migration(portal, http_request):
    def func(submit: bool = True):
        view = portal.restrictedTraverse("@@migrate_to_volto")
        if submit:
            http_request.form["form.submitted"] = True
        return view()

    return func


class TestMigrateToVolto:

    @pytest.fixture(autouse=True)
    def _setup(self, app, http_request, portal):
        self.app = app
        self.portal = portal
        self.request = http_request
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_form_renders(self, migration):
        html = migration(submit=False)
        assert "Migrate to Volto" in html

    def test_plonevolto_is_installed(self, installer, migration):
        assert installer.is_product_installed("plone.volto") is False
        migration()
        assert installer.is_product_installed("plone.volto") is True

    @pytest.mark.parametrize(
        "portal_type,id,title,klass",
        [
            ["Document", "doc", "Document", FolderishDocument],
            ["News Item", "news", "News Item", FolderishNewsItem],
            ["Event", "event", "Event", FolderishEvent],
        ],
    )
    def test_items_are_migrated_to_folderish(
        self, migration, portal_type, id, title, klass
    ):
        api.content.create(
            container=self.portal,
            type=portal_type,
            id=id,
            title=title,
        )
        migration()

        content = self.portal[id]
        assert content.portal_type == portal_type
        assert aq_base(content).isPrincipiaFolderish
        assert content.__class__ == klass

        # Test that doc renders without error.
        content.__call__()
        # We can add content
        sub_object = api.content.create(
            container=content,
            type="Document",
            id="subdoc",
            title="Sub Document",
        )
        assert sub_object.__class__ == FolderishDocument

    def test_folders_are_migrated(self, migration):
        api.content.create(
            container=self.portal,
            type="Folder",
            id="folder1",
            title="Folder 1",
        )
        assert self.portal["folder1"].portal_type == "Folder"

        migration()

        doc = self.portal["folder1"]
        assert doc.portal_type == "Document"
        assert aq_base(doc).isPrincipiaFolderish
        assert doc.__class__ == FolderishDocument

    def test_collections_are_migrated(self, migration):
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
        assert self.portal["collection"].portal_type == "Collection"

        migration()

        collection = self.portal["collection"]
        assert collection.portal_type == "Document"
        assert aq_base(collection).isPrincipiaFolderish
        assert collection.__class__ == FolderishDocument

        listing = collection.blocks[collection.blocks_layout["items"][1]]
        assert listing["@type"] == "listing"
        assert listing["querystring"] == {
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
        }

    def test_default_pages_are_migrated(self, migration):
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

        migration()

        folder = self.portal["folder"]
        assert folder.portal_type == "Document"
        assert getattr(folder, "default_page", None) is None
        assert folder.title == "Document"
        assert folder.description == "This is a default page"

    def test_default_page_collections_are_migrated(self, migration):
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
        assert "collection" in folder.keys()
        assert len(collection.results()) == 2

        migration()

        folder = self.portal["folder"]
        assert folder.portal_type == "Document"
        assert getattr(folder, "default_page", None) is None
        assert "collection" not in folder.keys()
        assert folder.title == "Collection"
        assert folder.description == "This is a default collection"
        listing = collection.blocks[collection.blocks_layout["items"][1]]
        assert listing["@type"] == "listing"
        assert listing["querystring"] == {
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
        }

    def test_default_page_news_are_not_migrated(self, migration):
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
        assert "news" in folder.keys()

        migration()

        folder = self.portal["folder"]
        assert folder.portal_type == "Document"
        # the default_page attr is not removed
        assert folder.default_page == "news"
        assert folder.title == "Folder"
        assert folder.description == "This of the folder"

        assert "news" in folder.keys()
        assert folder["news"].portal_type == "News Item"
        assert folder["news"].title == "News Item"
        assert folder["news"].description == "This is a default news item"

    @responses.activate
    def test_richtext_is_migrated(self, migration):
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
        assert isinstance(doc.text, RichTextValue)

        migration()

        doc = self.portal["doc"]
        assert doc.text is None
        uuid = doc.blocks_layout["items"][1]
        block = doc.blocks[uuid]
        assert block["plaintext"] == "I am html text"
