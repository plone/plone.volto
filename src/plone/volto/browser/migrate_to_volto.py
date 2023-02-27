from Acquisition import aq_base
from logging import getLogger
from plone import api
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.app.contenttypes.utils import get_old_class_name_string
from plone.app.contenttypes.utils import get_portal_type_name_string
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.volto.browser.migrate_richtext import get_blocks_from_richtext
from plone.volto.browser.migrate_richtext import migrate_richtext_to_blocks
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.relationhelper import restore_relations
from Products.CMFPlone.utils import get_installer
from Products.Five import BrowserView
from uuid import uuid4
from zope.component import getUtility
from zope.lifecycleevent import modified


try:
    from plone.app.contenttypes.utils import migrate_base_class_to_new_class
except ImportError:
    # BBB: Plone 5
    from plone.app.contenttypes.migration.dxmigration import (
        migrate_base_class_to_new_class,
    )

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
                try:
                    obj = brain.getObject()
                except Exception:
                    logger.info(
                        "Catalog inconsistent. Could not find %s",
                        brain.getPath(),
                        exc_info=True,
                    )
                    continue

                old_class_name = get_old_class_name_string(obj)
                new_class_name = get_portal_type_name_string(obj)
                is_container = isinstance(obj, BTreeFolder2Base)
                if old_class_name == new_class_name and is_container:
                    # we're already ok (maybe migration is running multiple times)
                    continue

                relations = export_relations(obj)
                migrate_base_class_to_new_class(obj, migrate_to_folderish=True)
                modified(obj)
                if relations:
                    restore_relations(all_relations=relations)

    def do_migrate_folders(self):
        """Migrate Folders to FolderisDocument."""
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type="Folder", sort_on="path"):
            obj = brain.getObject()
            obj = make_document(obj, slate=self.slate)
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
            obj = make_document(obj, slate=self.slate)

    def do_migrate_default_page(self, obj):
        """This assumes the obj is already a FolderishDocument"""
        default_page = None
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
        blocks = {}
        blocks_layout = {"items": []}

        if default_page_type in ["Collection", "Document"]:
            # richtext was already migrated in the first step
            # we reuse all blocks (except for title and description?)
            blocks = default_page_obj.blocks or blocks
            blocks_layout = default_page_obj.blocks_layout or blocks_layout

            if default_page_type == "Collection":
                uuid, block = generate_listing_block_from_collection(
                    default_page_obj, move_relative_path=True
                )
                blocks[uuid] = block
                blocks_layout["items"].append(uuid)

            # set title and description of the default page
            # the blocks for that are already there
            obj.title = default_page_obj.title
            obj.description = default_page_obj.description

            marker = object()
            for fieldname in [
                "subject",
                "rights",
                "creators",
                "contributors",
                "allow_discussion",
            ]:
                value = getattr(default_page_obj.aq_base, fieldname, marker)
                if value is not marker:
                    setattr(obj.aq_base, fieldname, value)

            relations = export_relations(default_page_obj)
            default_page_uid = default_page_obj.UID()
            old_path = "/".join(default_page_obj.getPhysicalPath())
            new_path = "/".join(obj.getPhysicalPath())

            # Delete the default page
            obj.manage_delObjects(default_page)

            # Add redirect from dropped default-page to container
            storage = getUtility(IRedirectionStorage)
            storage.add(old_path, new_path)

            # rewrite relations to point to parent
            fixed_relations = []
            obj_uid = obj.UID()
            for rel in relations:
                if default_page_uid == rel["from_uuid"]:
                    rel["from_uuid"] = obj_uid
                    fixed_relations.append(rel)
                if default_page_uid == rel["to_uuid"]:
                    rel["to_uuid"] = obj_uid
                    fixed_relations.append(rel)
            if fixed_relations:
                restore_relations(all_relations=fixed_relations)

        else:
            # We keep the default page in the new FolderishDocument
            # and only show a default listing block
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


def generate_listing_block_from_collection(obj, move_relative_path=False):
    """Transform collection query and setting to listing block."""
    collection = ICollection(obj)
    uuid = str(uuid4())
    if move_relative_path and collection.query:
        # when we migrate collections that were used as default-pages
        # with a relative path to the parent ("..::") that path now needs
        # to point to itself.
        for query_part in collection.query:
            if (
                "path" in query_part["i"]
                and "relativePath" in query_part["o"]
                and query_part["v"].startswith("..")
            ):
                query_part["v"] = query_part["v"].replace("..", ".", 1)
    qs = {"query": collection.query}
    if collection.item_count:
        qs["b_size"] = collection.item_count
    if collection.limit:
        qs["limit"] = collection.limit
    if collection.sort_on:
        qs["sort_on"] = collection.sort_on
    qs["sort_order"] = "descending" if collection.sort_reversed else "ascending"
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

    relations = export_relations(obj)
    migrate_base_class_to_new_class(
        obj,
        new_class_name="plone.volto.content.FolderishDocument",
    )
    # Drop any custom layout because Documents display blocks!
    if getattr(obj.aq_base, "layout", None) is not None:
        del obj.layout

    obj.portal_type = "Document"
    # Invalidate cache to find the behaviors
    if getattr(obj, "_v__providedBy__", None) is not None:
        del obj._v__providedBy__

    if not obj.blocks:
        obj.blocks = blocks
    else:
        obj.blocks.update(blocks)

    if not obj.blocks_layout["items"]:
        obj.blocks_layout = blocks_layout
    else:
        obj.blocks_layout["items"] += blocks_layout

    modified(obj)
    if relations:
        restore_relations(all_relations=relations)
    return obj


def export_relations(obj):
    results = []
    for rel in api.relation.get(target=obj, unrestricted=True):
        if rel.from_attribute == referencedRelationship:
            # drop linkintegrity
            continue
        results.append(
            {
                "from_uuid": rel.from_object.UID(),
                "to_uuid": rel.to_object.UID(),
                "from_attribute": rel.from_attribute,
            }
        )

    for rel in api.relation.get(source=obj, unrestricted=True):
        if rel.from_attribute == referencedRelationship:
            # drop linkintegrity
            continue
        results.append(
            {
                "from_uuid": rel.from_object.UID(),
                "to_uuid": rel.to_object.UID(),
                "from_attribute": rel.from_attribute,
            }
        )
    return results
