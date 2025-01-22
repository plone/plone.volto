from copy import deepcopy
from OFS.interfaces import IOrderedContainer
from plone import api
from plone.base.interfaces import IPloneSiteRoot
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.restapi.behaviors import IBlocks
from plone.volto import content
from plone.volto import logger
from plone.volto.setuphandlers import NO_RICHTEXT_BEHAVIOR_CONTENT_TYPES
from plone.volto.setuphandlers import remove_behavior
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility

import transaction


MIGRATION = {
    "Document": content.FolderishDocument,
    "Event": content.FolderishEvent,
    "News Item": content.FolderishNewsItem,
}


def migrate_content_classes(context):
    """Migrate content created with collective.folderishtypes to plone.volto."""
    interface = "collective.folderishtypes.interfaces.IFolderishType"
    idxs = ["object_provides", "getObjPositionInParent"]
    brains = api.content.find(
        object_provides=interface, sort_on="getObjPositionInParent"
    )
    total_brains = len(brains)
    logger.info(f"Migration: {total_brains} contents to be migrated.")
    for idx, brain in enumerate(brains):
        content = brain.getObject()
        content_id = content.getId()
        content.__class__ = MIGRATION[content.portal_type]
        parent = content.aq_parent
        ordered = IOrderedContainer(parent, None)
        if ordered is not None:
            order = ordered.getObjectPosition(content.getId())
            if order == 1:
                # can be the default one and we will lose the ordering
                order = ordered.keys().index(content.getId())
        parent._delOb(content_id)
        parent._setOb(content_id, content)
        content = parent[content_id]
        ordered.moveObjectToPosition(content.getId(), order)
        content.reindexObject(idxs=idxs)

        if idx and idx % 100 == 0:
            logger.info(f"Migration: {idx + 1} / {total_brains}")

    logger.info("Migration from collective.folderishtypes to plone.volto complete")


def from12to13_migrate_listings(context):
    def migrate_listing(originBlocks):
        blocks = deepcopy(originBlocks)
        for blockid in blocks:
            block = blocks[blockid]
            if block["@type"] == "listing":
                if block.get("template", False) and not block.get("variation", False):
                    block["variation"] = block["template"]
                    del block["template"]
                if block.get("template", False) and block.get("variation", False):
                    del block["template"]

                # Migrate to internal structure
                if not block.get("querystring", False):
                    # Creates if it is not created
                    block["querystring"] = {}
                if block.get("query", False) or block.get("query") == []:
                    block["querystring"]["query"] = block["query"]
                    del block["query"]
                if block.get("sort_on", False):
                    block["querystring"]["sort_on"] = block["sort_on"]
                    del block["sort_on"]
                if block.get("sort_order", False):
                    block["querystring"]["sort_order"] = block["sort_order"]
                    if isinstance(block["sort_order"], bool):
                        block["querystring"]["sort_order"] = (
                            "descending" if block["sort_order"] else "ascending"
                        )
                    else:
                        block["querystring"]["sort_order"] = block["sort_order"]
                    block["querystring"]["sort_order_boolean"] = (
                        True
                        if block["sort_order"] == "descending" or block["sort_order"]
                        else False
                    )
                    del block["sort_order"]
                if block.get("limit", False):
                    block["querystring"]["limit"] = block["limit"]
                    del block["limit"]
                if block.get("batch_size", False):
                    block["querystring"]["batch_size"] = block["batch_size"]
                    del block["batch_size"]
                if block.get("depth", False):
                    block["querystring"]["depth"] = block["depth"]
                    del block["depth"]

                # batch_size to b_size, idempotent
                if block["querystring"].get("batch_size", False):
                    block["querystring"]["b_size"] = block["querystring"]["batch_size"]
                    del block["querystring"]["batch_size"]

                print(f"Migrated listing in {obj.absolute_url()}")

        return blocks

    pc = api.portal.get_tool("portal_catalog")
    for brain in pc.unrestrictedSearchResults(object_provides=IBlocks.__identifier__):
        obj = brain.getObject()
        obj.blocks = migrate_listing(obj.blocks)


def remove_plone_richtext_behavior(context):
    for type_ in NO_RICHTEXT_BEHAVIOR_CONTENT_TYPES:
        remove_behavior(type_, "plone.richtext")


def add_control_panel_classic_icon(context):
    registry = getUtility(IRegistry)
    registry.records["plone.icon.volto-settings"] = Record(
        field.TextLine(title="Plone Icon Volto Control Panel"),
    )
    registry["plone.icon.volto-settings"] = "++plone++plone.volto/volto.svg"


def add_block_types_index(context):
    catalog = getToolByName(context, "portal_catalog")
    indexes = catalog.indexes()
    if "block_types" not in indexes:
        catalog.addIndex("block_types", "KeywordIndex")
        logger.info("Added block_types index.")
    brains = catalog(object_provides="plone.restapi.behaviors.IBlocks")
    total = len(brains)
    for index, brain in enumerate(brains):
        obj = brain.getObject()
        obj.reindexObject(idxs=["block_types"], update_metadata=0)
        logger.info("Reindexing object %s.", brain.getPath())
        if index % 250 == 0:
            logger.info(f"Reindexed {index}/{total} objects")
            transaction.commit()


def rename_distribution(context):
    from plone.distribution.api.distribution import get_creation_report

    portal = getUtility(IPloneSiteRoot)
    report = get_creation_report(portal)
    if report is not None:
        if report.name == "default":
            report.name = "volto"
        if report.answers.get("distribution") == "default":
            report.answers["distribution"] = "volto"


ROBOTS_TXT = """Sitemap: {portal_url}/sitemap-index.xml

# Define access-restrictions for robots/spiders
# http://www.robotstxt.org/wc/norobots.html

User-agent: *
Disallow: /search
Disallow: /login

# Add Googlebot-specific syntax extension to exclude forms
# that are repeated for each piece of content in the site
# the wildcard is only supported by Googlebot
# http://www.google.com/support/webmasters/bin/answer.py?answer=40367&ctx=sibling

User-Agent: Googlebot
Disallow: /*login
Disallow: /*search
Disallow: /*edit
"""


def update_robots_txt(context):
    from plone.base.interfaces.controlpanel import ROBOTS_TXT as CLASSIC_ROBOTS

    current_value = api.portal.get_registry_record("plone.robots_txt")
    if current_value == CLASSIC_ROBOTS:
        api.portal.set_registry_record("plone.robots_txt", ROBOTS_TXT)
        logger.info("Updated plone.robots_txt registry with sane value.")
    else:
        logger.info(
            "Ignoring plone.robots_txt registry as it was modified in this portal."
        )
