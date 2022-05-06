from Acquisition import aq_base
from logging import getLogger
from plone import api
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.utils import migrate_base_class_to_new_class
from plone.app.textfield.value import RichTextValue
from plone.base.utils import get_installer
from plone.dexterity.interfaces import IDexterityFTI
from plone.volto.browser.migrate_richtext import get_blocks_from_richtext
from plone.volto.browser.migrate_richtext import migrate_richtext_to_blocks
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility
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
        self.migrate_default_pages = request.get("migrate_default_pages", True)
        self.purge_richtext = request.get("purge_richtext", True)
        # We still use draftjs at the moment
        self.slate = request.get("slate", False)

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

        self.migrate_collections()

        self.enable_leadimage_block()

        api.portal.show_message("Finished migration to Volto!", self.request)
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
            obj = make_document(obj, slate=self.slate)
            parent = obj.__parent__
            migrated_default_page = False
            if self.migrate_default_pages:
                migrated_default_page = self.do_migrate_default_page(obj)
            if not migrated_default_page:
                uuid, block = generate_listing_block(obj)
                obj.blocks[uuid] = block
                obj.blocks_layout["items"].append(uuid)
                obj._p_changed = True

    def migrate_collections(self):
        """Migrate Collections to FolderisDocument with Listing Blocks
        Collections that are default pages are already removed when this runs.
        """
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type="Collection", sort_on="path"):
            obj = brain.getObject()
            # TODO: Migrate richtext (not done by convert_richtext because plone.blocks is not enabled!)
            obj = make_document(obj, slate=self.slate)

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
                text_blocks, uuids = get_blocks_from_richtext(text, slate=self.slate)
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
        return True

    def convert_richtext(self):
        """Get richtext for all content that has it and set as blocks."""
        migrate_richtext_to_blocks(
            service_url=self.service_url,
            purge_richtext=self.purge_richtext,
            slate=self.slate,
        )

    def installed_addons(self):
        results = []
        installer = get_installer(self.context, self.request)
        for profile_id in installer.get_install_profiles():
            if installer.is_profile_installed(profile_id):
                results.append(profile_id)
        return results

    def enable_leadimage_block(self):
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(object_provides=ILeadImage.__identifier__):
            obj = brain.getObject()
            if ILeadImage(obj).image:
                uuid = str(uuid4())
                obj.blocks_layout["items"].insert(1, uuid)
                obj.blocks[uuid] = {"@type": "leadimage"}
                obj._p_changed = True


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
        "querystring": qs,
        "variation": variation,
        "block": uuid,
    }
    return uuid, block


def make_document(obj, slate=True):
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

    fti = getUtility(IDexterityFTI, name=obj.portal_type)
    # When volto.blocks is there was alrady done by migrate_richtext
    # This happens with Collections
    if "volto.blocks" not in fti.behaviors:
        text = getattr(obj.aq_base, "text", None)
        if isinstance(text, RichTextValue):
            text = text.raw
        if text and text.strip():
            # We have Richtext. Get the block-data for it
            text_blocks, uuids = get_blocks_from_richtext(text, slate=slate)
            if uuids:
                blocks.update(text_blocks)
                blocks_layout["items"] += uuids

    if obj.portal_type == "Collection":
        uuid, block = generate_listing_block_from_collection(obj)
        blocks[uuid] = block
        blocks_layout["items"].append(uuid)

    migrate_base_class_to_new_class(
        obj,
        new_class_name="plone.volto.content.FolderishDocument",
    )
    # Drop any custom layout because Documents display blocks!
    if getattr(obj.aq_base, "layout", None) is not None:
        del obj.layout

    obj.portal_type = "Document"
    # Invalidate cache to find the behaviors
    del obj._v__providedBy__

    if not obj.blocks:
        obj.blocks = blocks
    else:
        obj.blocks.update(blocks)

    if not obj.blocks_layout["items"]:
        obj.blocks_layout = blocks_layout
    else:
        obj.blocks_layout["items"] += blocks_layout

    obj._p_changed = True
    obj.reindexObject(idxs=["SearchableText"])
    return obj
