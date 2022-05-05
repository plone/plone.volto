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
        self.migrate_default_pages = request.get("migrate_default_pages", True)
        self.purge_richtext = request.get("purge_richtext", True)

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

        self.request.response.redirect(self.context.absolute_url())

    def install_plone_volto(self):
        installer = get_installer(self.context, self.request)
        installer.install_product("plone.volto")
        transaction.commit()

    def migrate_to_folderish(self):
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
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type="Folder", sort_on="path"):
            obj = brain.getObject()
            parent = obj.__parent__
            migrate_base_class_to_new_class(
                obj,
                old_class_name="plone.app.contenttypes.content.Folder",
                # TODO: Change klass to plone.app.contenttypes.content.FolderishDocument?
                new_class_name="plone.volto.content.FolderishDocument",
            )
            # TODO: Set various attributes and behaviors
            obj = parent[brain.id]
            obj.portal_type = "Document"
            # Invalidate cache to find the behaviors
            del obj._v__providedBy__
            if self.migrate_default_pages:
                self.do_migrate_default_page(obj)
            obj._p_changed = True

    def do_migrate_default_page(self, obj):
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
                listing_block_uuid, listing_block = generate_listing_block_from_query(
                    default_page_obj
                )
                # TODO: Set layout of collection to listing block (mapping needed?)
                blocks[listing_block_uuid] = listing_block
                blocks_layout["items"].append(listing_block_uuid)

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
        migrate_richtext_to_blocks(
            service_url=self.service_url,
            purge_richtext=self.purge_richtext,
        )

    def installed_addons(self):
        results = []
        installer = get_installer(self.context, self.request)
        for profile_id in installer.get_install_profiles():
            if installer.is_profile_installed(profile_id):
                results.append(profile_id)
        return results


def generate_listing_block(obj):
    uuid = str(uuid4())
    query = [
        {
            "i": "path",
            "o": "plone.app.querystring.operation.string.path",
            "v": f"{obj.UID()}::1",
        }
    ]
    block = {
        "@type": "listing",
        "query": query,
        "sort_on": "getObjPositionInParent",
        "sort_order": False,
        "b_size": "30",
        "block": uuid,
    }
    return uuid, block


def generate_listing_block_from_query(obj):
    collection = ICollection(obj)
    uuid = str(uuid4())
    block = {
        "@type": "listing",
        "query": collection.query,
        "sort_on": getattr(collection, "sort_on", "getObjPositionInParent"),
        "sort_order": getattr(collection, "sort_reversed", False),
        "b_size": getattr(collection, "item_count", "30"),
        "block": uuid,
    }
    return uuid, block
