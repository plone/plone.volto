from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError
from plone import api
from plone.base.interfaces import INonInstallable
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from zope.interface import implementer

import transaction


try:
    distribution("plone.app.multilingual")
    from plone.app.multilingual.browser.setup import SetupMultilingualSite
    from plone.app.multilingual.setuphandlers import enable_translatable_behavior

    HAS_MULTILINGUAL = True
except PackageNotFoundError:
    HAS_MULTILINGUAL = False


NO_RICHTEXT_BEHAVIOR_CONTENT_TYPES = [
    "Plone Site",
    "Document",
    "News Item",
    "Event",
]


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            "plone.volto:uninstall",
        ]


def post_install(context):
    """Post install script"""
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


def enable_pam(portal):
    if HAS_MULTILINGUAL:
        # Ensure that portal is portal
        portal = api.portal.get()
        # Setup the plone.app.multilingual data
        sms = SetupMultilingualSite(portal)
        sms.setupSite(portal)
        enable_translatable_behavior(portal)


def ensure_pam_consistency(portal):
    """Makes sure that all the content in a language branch has language"""

    # Ensure that all the objects below an LFR is of the intended language
    pc = api.portal.get_tool("portal_catalog")
    pl = api.portal.get_tool("portal_languages")

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
    portal_types = api.portal.get_tool("portal_types")
    news_item_fti = getattr(portal_types, old_name)
    news_item_fti.title = new_name


def disable_content_type(portal, fti_id):
    portal_types = api.portal.get_tool("portal_types")
    document_fti = getattr(portal_types, fti_id, False)
    if document_fti:
        document_fti.global_allow = False


def enable_content_type(portal, fti_id):
    portal_types = api.portal.get_tool("portal_types")
    document_fti = getattr(portal_types, fti_id, False)
    if document_fti:
        document_fti.global_allow = True


def copy_content_type(portal, name, newid, newname):
    """Create a new content type by copying an existing one"""
    portal_types = api.portal.get_tool("portal_types")
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
