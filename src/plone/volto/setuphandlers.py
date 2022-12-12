# -*- coding: utf-8 -*-
from importlib import import_module
from plone import api
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.setuphandlers import enable_translatable_behavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.volto.default_homepage.default import default_home
from plone.volto.default_homepage.demo import demo_home_page
from plone.volto.default_homepage.lrf import default_lrf_home
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.utils import get_installer
from zope.component import queryUtility
from zope.interface import implementer

import json
import logging
import transaction


PLONE_6 = getattr(import_module("Products.CMFPlone.factory"), "PLONE60MARKER", False)

logger = logging.getLogger("plone.volto")

NO_RICHTEXT_BEHAVIOR_CONTENT_TYPES = [
    "Plone Site",
    "Document",
    "News Item",
    "Event",
]


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            "plone.volto:uninstall",
        ]


def post_install(context):
    """Post install script"""
    # For Plone 6, make sure the blocks behavior is enabled in the root
    if PLONE_6:
        add_behavior("Plone Site", "volto.blocks")
    else:
        set_edit_action_in_plone_site_for_plone5(context)

    # Remove plone.richtext from content types with blocks enabled
    for type_ in NO_RICHTEXT_BEHAVIOR_CONTENT_TYPES:
        remove_behavior(type_, "plone.richtext")


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def post_install_coresandbox(context):
    """Post install script for multilingual fixture"""


def post_install_multilingual(context):
    """Post install script for multilingual fixture"""
    enable_pam(context)
    create_default_homepage(context)


def enable_pam(portal):
    # Ensure that portal is portal
    portal = api.portal.get()
    # Setup the plone.app.multilingual data
    sms = SetupMultilingualSite(portal)
    sms.setupSite(portal)
    enable_translatable_behavior(portal)


def ensure_pam_consistency(portal):
    """Makes sure that all the content in a language branch has language"""

    # Ensure that all the objects below an LFR is of the intended language
    pc = getToolByName(portal, "portal_catalog")
    pl = getToolByName(portal, "portal_languages")

    supported_langs = pl.getSupportedLanguages()

    for lang in supported_langs:
        objects = pc.searchResults(path={"query": f"/Plone/{lang}"})

        for brain in objects:
            obj = brain.getObject()
            if not obj.language or obj.language != lang:
                print(f"Setting missing lang to object: {obj.absolute_url()}")
                obj.language = lang

    pc.clearFindAndRebuild()

    transaction.commit()


def change_content_type_title(portal, old_name, new_name):
    """
    change_content_type_title(portal, 'News Item', 'Meldung')
    """
    portal_types = getToolByName(portal, "portal_types")
    news_item_fti = getattr(portal_types, old_name)
    news_item_fti.title = new_name


def disable_content_type(portal, fti_id):
    portal_types = getToolByName(portal, "portal_types")
    document_fti = getattr(portal_types, fti_id, False)
    if document_fti:
        document_fti.global_allow = False


def enable_content_type(portal, fti_id):
    portal_types = getToolByName(portal, "portal_types")
    document_fti = getattr(portal_types, fti_id, False)
    if document_fti:
        document_fti.global_allow = True


def copy_content_type(portal, name, newid, newname):
    """Create a new content type by copying an existing one"""
    portal_types = getToolByName(portal, "portal_types")
    tmp_obj = portal_types.manage_copyObjects([name])
    tmp_obj = portal_types.manage_pasteObjects(tmp_obj)
    tmp_id = tmp_obj[0]["new_id"]
    new_type_fti = getattr(portal_types, tmp_id)
    new_type_fti.title = newname
    portal_types.manage_renameObjects([tmp_id], [newid])


def add_catalog_indexes(context, wanted=None):
    """Method to add our wanted indexes to the portal_catalog."""
    catalog = api.portal.get_tool("portal_catalog")
    indexes = catalog.indexes()
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
    if len(indexables) > 0:
        catalog.manage_reindexIndex(ids=indexables)


def add_behavior(portal_type, behavior):
    fti = queryUtility(IDexterityFTI, name=portal_type)
    if fti is not None:
        # This prevents to add the behavior twice
        new = [
            currentbehavior
            for currentbehavior in fti.behaviors
            if currentbehavior != behavior
        ]
        new.append(behavior)
        fti.behaviors = tuple(new)


def remove_behavior(portal_type, behavior):
    fti = queryUtility(IDexterityFTI, name=portal_type)
    if fti is not None:
        new = [
            currentbehavior
            for currentbehavior in fti.behaviors
            if currentbehavior != behavior
        ]
        fti.behaviors = tuple(new)


def set_edit_action_in_plone_site_for_plone5(context):
    pt = api.portal.get_tool("portal_types")
    fti = pt.getTypeInfo("Plone Site")

    # Plone site Edit action properties
    action_id = "edit"
    category = "object"
    condition = ""
    title = "Edit"
    action = "string:${object_url}/edit"
    visible = "True"
    permissions = ["Modify portal content"]
    icon_expr = ""
    link_target = ""

    action_obj = fti.getActionObject(category + "/" + action_id)

    if action_obj is None:
        fti.addAction(
            action_id,
            title,
            action,
            condition,
            tuple(permissions),
            category,
            visible,
            icon_expr=icon_expr,
            link_target=link_target,
        )
    else:
        action_obj.edit(
            title=title,
            action=action,
            icon_expr=icon_expr,
            condition=condition,
            permissions=tuple(permissions),
            visible=visible,
            link_target=link_target,
        )


def create_default_homepage_draftjs(context):
    create_default_homepage(context, block_type="draftJS")


def create_default_homepage_slate(context):
    create_default_homepage(context, block_type="slate")


def create_default_homepage(context, default_home=default_lrf_home, block_type=None):
    """This method allows to pass a dict with the homepage blocks and blocks_layout keys"""
    portal = api.portal.get()
    # Test for PAM installed
    try:
        is_pam_installed = get_installer(portal, context.REQUEST).isProductInstalled(
            "plone.app.multilingual"
        )
    except:  # noqa
        is_pam_installed = get_installer(portal, context.REQUEST).is_product_installed(
            "plone.app.multilingual"
        )

    if is_pam_installed:
        # Make sure that the LRFs have the blocks enabled
        add_behavior("LRF", "volto.blocks")

        if block_type and block_type in default_home:
            home_data = default_home[block_type]
        else:
            # Default to slate
            home_data = default_home["slate"]

        for lang in api.portal.get_registry_record("plone.available_languages"):
            # Do not write them if there are blocks set already
            # Get the attr first, in case it's not there yet (error in docker image)
            if getattr(portal[lang], "blocks", {}) == {} and (
                getattr(portal[lang], "blocks_layout", {}).get("items") is None
                or getattr(portal[lang], "blocks_layout", {}).get("items") == []
            ):
                logger.info(
                    "Creating default homepage for {} - PAM enabled".format(lang)
                )
                portal[lang].blocks = home_data["blocks"]
                portal[lang].blocks_layout = home_data["blocks_layout"]

    else:
        create_root_homepage(context, block_type)


def create_root_homepage(context, block_type=None, default_home=default_home):
    """It takes a default object:
    {
        "title": "The title",
        "description": "The description",
        "blocks": {...},
        "blocks_layout": [...]
    }
    and sets it as default page in the Plone root object.

    Takes into account block_type.
    """
    portal = api.portal.get()

    if block_type and block_type in default_home:
        home_data = default_home[block_type]
    else:
        # Default to slate
        home_data = default_home["slate"]

    logger.info(
        f"Creating default homepage in Plone {'6' if PLONE_6 else ''} site root with {block_type} blocks - not PAM enabled"
    )

    if PLONE_6:
        portal.blocks = home_data["blocks"]
        portal.blocks_layout = home_data["blocks_layout"]
        portal.title = home_data["title"]
        if home_data.get("description"):
            portal.description = home_data["description"]
    else:
        blocks = home_data["blocks"]
        blocks_layout = home_data["blocks_layout"]
        portal.setTitle(home_data["title"])
        if home_data.get("description"):
            portal.setDescription(home_data["description"])

        # Use the hack for setting the home page in Plone Site object
        if not getattr(portal, "blocks", False):
            portal.manage_addProperty("blocks", json.dumps(blocks), "string")

        if not getattr(portal, "blocks_layout", False):
            portal.manage_addProperty(
                "blocks_layout", json.dumps(blocks_layout), "string"
            )  # noqa


def create_demo_homepage(context):
    create_root_homepage(context, default_home=demo_home_page)
