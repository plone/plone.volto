from Acquisition import aq_base
from logging import getLogger
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.utils import migrate_base_class_to_new_class
from plone.app.textfield.value import RichTextValue
from plone.base.utils import get_installer
from plone.volto.browser.migrate_richtext import migrate_richtext_to_blocks
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from uuid import uuid4

import requests
import transaction

logger = getLogger(__name__)


class MigrateToVolto(BrowserView):
    """Basically a configurable upgrade-step to prepare a existing site for Volto."""

    def __call__(self):
        request = self.request
        self.service_url = request.get("service_url", "http://localhost:5000/html")
        self.migrate_folders = request.get("migrate_folders", True)
        self.migrate_collections = request.get("migrate_collections", True)
        self.migrate_default_pages = request.get("migrate_default_pages", True)
        self.purge_richtext = request.get("purge_richtext", True)
        self.convert_to_slate = request.get("convert_to_slate", False)

        if not self.request.form.get("form.submitted", False):
            return self.index()

        # 1. Install plone volto to enable plone.blocks behavior and change klass on fti
        self.install_plone_volto()

        # 2. Migrate to Slate
        self.convert_richtext()

        # 3. Migrate existing content where fti.klass != obj.__class__
        self.migrate_to_folderish()

        if self.migrate_folders:
            self.do_migrate_folders()

        if self.migrate_collections:
            self.do_migrate_collections()

        self.request.response.redirect(self.context.absolute_url())

    def install_plone_volto(self):
        installer = get_installer(self.context, self.request)
        installer.install_product("plone.volto")

    def migrate_to_folderish(self):
        """Migrate default itemish content to folderish"""
        folderish_types = [
            "Document",
            "Event",
            "News Item",
        ]
        catalog = getToolByName(self.context, "portal_catalog")
        for portal_type in folderish_types:
            for brain in catalog(portal_type=portal_type, sort_on="path"):
                obj = brain.getObject()
                migrate_base_class_to_new_class(obj, migrate_to_folderish=True)

    def do_migrate_folders(self):
        """Migrate Folders to FolderisDocument."""
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type="Folder", sort_on="path"):
            obj = brain.getObject()
            obj = make_document(obj, self.service_url)
            parent = obj.__parent__
            if self.migrate_default_pages:
                self.do_migrate_default_page(obj)

    def do_migrate_collections(self):
        """Migrate Collections to FolderisDocument with Listing Blocks
        Collections that are default pages are already removed when this runs.
        """
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type="Collection", sort_on="path"):
            obj = brain.getObject()
            obj = make_document(obj, self.service_url)

    def do_migrate_default_page(self, obj):
        """This assumes the obj is already a FolderishDocument"""
        default_page = None
        blocks = {}
        blocks_layout = {"items": []}
        if "index_html" in obj:
            # 1. Check for a index_html item in it
            default_page = "index_html"
        else:
            # 2. Check attribute 'default_page'
            default_page = getattr(aq_base(obj), "default_page", [])

        if not default_page or default_page not in obj:
            return

        default_page_obj = obj.get(default_page)
        default_page_type = default_page_obj.portal_type

        if default_page_type in ["Collection", "Document"]:
            # Handle Richtext
            text = getattr(default_page_obj.aq_base, "text", None)
            if isinstance(text, RichTextValue):
                text = text.raw
            if text and text.strip():
                # We have Richtext. Get the block-data for it
                text_blocks, uuids = self.get_blocks_from_richtext(text)
                if uuids:
                    blocks.update(text_blocks)
                    blocks_layout["items"] += uuids

            if default_page_type == "Collection":
                uuid, block = generate_listing_block_from_collection(default_page_obj)
                blocks[uuid] = block
                blocks_layout["items"].append(uuid)

            # set title for default page
            obj.title = default_page_obj.title
            uuid = str(uuid4())
            blocks[uuid] = {"@type": "title"}
            blocks_layout["items"].insert(0, uuid)

            # set description of default page
            obj.description = default_page_obj.description
            if obj.description:
                uuid = str(uuid4())
                blocks[uuid] = {"@type": "description"}
                blocks_layout["items"].insert(1, uuid)

            # TODO: Move to obj: Subjects, Creator, Dates, Constributor, Rights
            # TODO: Add redirect from dropped default-page to container
            # TODO: Recreate relations that pointed to the dropped default page

            # Delete the default page
            obj.manage_delObjects(default_page)

        else:
            # We keep the default page in the new FolderishDocument
            # and show a default listing block
            uuid, block = generate_listing_block(obj)
            blocks[uuid] = block
            blocks_layout["items"].append(uuid)

        obj.blocks = blocks
        obj.blocks_layout = blocks_layout
        obj._p_changed = True
        obj.reindexObject(idxs=["SearchableText"])

    def get_blocks_from_richtext(self, text):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {"html": text}
        if not self.convert_to_slate:
            # TODO: remove this when slate is merged
            payload["converter"] = "draftjs"
        r = requests.post(self.service_url, headers=headers, json=payload)
        r.raise_for_status()
        slate_data = r.json()
        slate_data = slate_data["data"]
        blocks = {}
        uuids = []
        # generate slate blocks
        for block in slate_data:
            uuid = str(uuid4())
            uuids.append(uuid)
            blocks[uuid] = block
        return blocks, uuids

    def convert_richtext(self):
        """Get richtext for all content that has it and set as blocks.
        TODO: This will override any blocks that alreaduy exist. Handle that?
        """
        migrate_richtext_to_blocks(
            service_url=self.service_url,
            purge_richtext=self.purge_richtext,
            convert_to_slate=False,
        )

    def installed_addons(self):
        results = []
        installer = get_installer(self.context, self.request)
        for profile_id in installer.get_install_profiles():
            if installer.is_profile_installed(profile_id):
                results.append(profile_id)
        return results


def generate_listing_block(obj):
    # List content of this container
    uuid = str(uuid4())
    block = {
        "@type": "listing",
        "query": [],
        "variation": "default",
        "block": uuid,
    }
    return uuid, block


def generate_listing_block_from_collection(obj):
    """Transform collection query and setting to listing block."""
    collection = ICollection(obj)
    uuid = str(uuid4())
    qs = {"query": collection.query}
    if collection.item_count:
        qs["b_size"] = collection.item_count
    if collection.limit:
        qs["limit"] = collection.limit
    if collection.sort_on:
        qs["sort_on"] = collection.sort_on
    qs["sort_order_boolean"] = True if collection.sort_reversed else False

    # Set layout of collection to listing block
    # TODO: What about event_listing, tabular_view and full_view?
    variation_mapping = {
        "listing_view": "default",
        "summary_view": "summary",
        "album_view": "imageGallery",
    }
    variation = variation_mapping.get(obj.getLayout, "default")
    block = {
        "@type": "listing",
        "query": [],
        "querystring": qs,
        "variation": variation,
        "block": uuid,
    }
    return uuid, block


def make_document(obj, service_url="http://localhost:5000/html"):
    """Convert any item to a FolderishDocument"""
    blocks = {}
    blocks_layout = {"items": []}

    # set title
    obj.title = obj.title
    uuid = str(uuid4())
    blocks[uuid] = {"@type": "title"}
    blocks_layout["items"].insert(0, uuid)

    # set description
    if obj.description:
        uuid = str(uuid4())
        blocks[uuid] = {"@type": "description"}
        blocks_layout["items"].insert(1, uuid)

    if obj.portal_type == "Collection":
        uuid, block = generate_listing_block_from_collection(obj)
        blocks[uuid] = block
        blocks_layout["items"].append(uuid)

    migrate_base_class_to_new_class(
        obj,
        new_class_name="plone.volto.content.FolderishDocument",
    )
    obj.portal_type = "Document"
    # Invalidate cache to find the behaviors
    del obj._v__providedBy__

    obj.blocks = blocks
    obj.blocks_layout = blocks_layout
    obj._p_changed = True
    obj.reindexObject(idxs=["SearchableText"])
    return obj
