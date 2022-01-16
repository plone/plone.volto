# -*- coding: utf-8 -*-
from datetime import datetime
from plone import api
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.setuphandlers import enable_translatable_behavior
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.dexterity.interfaces import IDexterityFTI
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.CMFPlone.utils import get_installer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.interfaces import IFactory
from zope.container.interfaces import INameChooser
from zope.interface import implementer

import json
import logging
import transaction

try:
    from Products.CMFPlone.factory import PLONE60MARKER

    PLONE60MARKER  # pyflakes
except ImportError:
    PLONE_6 = False
else:
    PLONE_6 = True

logger = logging.getLogger("plone.volto")


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return ["plone.volto:uninstall"]


def post_install(context):
    """Post install script"""
    # For Plone 6, make sure the blocks behavior is enabled in the root
    if PLONE_6:
        add_behavior("Plone Site", "volto.blocks")


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
    new = [
        currentbehavior
        for currentbehavior in fti.behaviors
        if currentbehavior != behavior
    ]
    new.append(behavior)
    fti.behaviors = tuple(new)


def setupNavigationPortlet(
    context,
    name="",
    root=None,
    includeTop=False,
    currentFolderOnly=False,
    bottomLevel=0,
    topLevel=0,
):
    """
    setupNavigationPortlet(portal['vereinigungen']['fachliche-vereinigungen']['sektion-materie-und-kosmos']['gravitation-und-relativitaetstheorie']) # noqa
    """
    from plone.app.portlets.portlets.navigation import (
        Assignment as NavAssignment,
    )  # noqa

    target_manager = queryUtility(
        IPortletManager, name="plone.leftcolumn", context=context
    )
    target_manager_assignments = getMultiAdapter(
        (context, target_manager), IPortletAssignmentMapping
    )

    navtree = NavAssignment(
        includeTop=includeTop,
        currentFolderOnly=currentFolderOnly,
        bottomLevel=bottomLevel,
        topLevel=topLevel,
    )

    if "navigation" not in target_manager_assignments.keys():
        target_manager_assignments["navigation"] = navtree


def setupPortletAt(portal, portlet_type, manager, path, name="", **kw):
    """
    setupPortletAt(portal, 'portlets.Events', 'plone.rightcolumn', '/vereinigungen/fachliche-vereinigungen/sektion-kondensierte-materie/halbleiterphysik') # noqa
    """
    portlet_factory = getUtility(IFactory, name=portlet_type)
    assignment = portlet_factory(**kw)
    mapping = assignment_mapping_from_key(
        portal, manager, CONTEXT_CATEGORY, path, create=True
    )

    if not name:
        chooser = INameChooser(mapping)
        name = chooser.chooseName(None, assignment)

    mapping[name] = assignment


default_home = {
    "draftJS": {
        "title": "Welcome to Volto!",
        "description": "The React powered content management system",
        "blocks": {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {"@type": "description"},
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "2dfe8e4c-5bf6-43f1-93e1-6c320ede7226": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 10, "offset": 0, "style": "BOLD"}
                            ],
                            "key": "6470b",
                            "text": "Disclaimer: This instance is reset every night, so all changes will be lost afterwards.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "3c881f51-f75b-4959-834a-6e1d5edc32ae": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 5, "offset": 6, "style": "BOLD"}
                            ],
                            "key": "ekn3l",
                            "text": "user: admin",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "5e1c30b1-ec6c-4dc0-9483-9768c3c416e4": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [
                                {"key": 0, "length": 5, "offset": 0},
                                {"key": 1, "length": 8, "offset": 455},
                            ],
                            "inlineStyleRanges": [],
                            "key": "behki",
                            "text": "Plone is a CMS built on Python with over 19 years of experience. Plone has very interesting features that appeal to developers and users alike, such as customizable content types, hierarchical URL object traversing and a sophisticated content workflow powered by a granular permissions model. This allows you to build anything from simple websites to enterprise-grade intranets. Volto exposes all these features and communicates with Plone via its mature REST API. Volto can be esily themed and is highly customizable.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": "https://plone.org",
                                "rel": "nofollow",
                                "url": "https://plone.org/",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        },
                        "1": {
                            "data": {
                                "href": "https://github.com/plone/plone.restapi",
                                "url": "https://github.com/plone/plone.restapi",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        },
                    },
                },
            },
            "61cc1bc0-d4f5-4e2b-9152-79512045a4dd": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "9qsa4",
                            "text": "Demo",
                            "type": "header-two",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "874049e7-629e-489a-b46c-1adf35ad40ee": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "9pnjr",
                            "text": "Happy hacking!",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "942b6530-2407-420f-9c24-597adda6b2ce": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 36, "offset": 39}],
                            "inlineStyleRanges": [],
                            "key": "6a248",
                            "text": "Last but not least, it also supports a Volto Nodejs-based backend reference API implementation that demos how other systems could also use Volto to display and create content through it.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": "https://github.com/plone/volto-reference-backend",
                                "url": "https://github.com/plone/volto-reference-backend",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
            "9a976b8e-72ba-468a-bea8-b37a31bb386b": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 12, "offset": 51, "style": "BOLD"}
                            ],
                            "key": "94arl",
                            "text": "You can log in and use it as admin user using these credentials:",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "b3717238-448f-406e-b06f-57a9715c3326": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "1bnna",
                            "text": "Volto is a React-based frontend for content management systems, currently supporting three backend implementations: Plone, Guillotina and a NodeJS reference implementation.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": "https://github.com/plone/volto",
                                "url": "https://github.com/plone/volto",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
            "c049ff8b-3e5a-4cfb-bca6-e4a6cca9be28": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "55n44",
                            "text": "You can use this site to test Volto. It runs on the master branch of Volto using latest Plone 5.2 Backend running on Python 3.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "c91f0fe9-f2e9-4a17-84a5-8e4f2678ed3c": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 5, "offset": 10, "style": "BOLD"}
                            ],
                            "key": "buncq",
                            "text": "password: admin",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "e0ca2fbc-7800-4b9b-afe5-8e42af9f5dd6": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "f0prj",
                            "text": f"{datetime.now().year} - Volto Team - Plone Foundation",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 10, "offset": 36}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "Volto also supports other APIs like Guillotina, a Python resource management system, inspired by Plone and using the same basic concepts like traversal, content types and permissions model.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": "https://guillotina.io/",
                                "rel": "nofollow",
                                "url": "https://guillotina.io/",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
        },
        "blocks_layout": {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19",
                "b3717238-448f-406e-b06f-57a9715c3326",
                "5e1c30b1-ec6c-4dc0-9483-9768c3c416e4",
                "effbdcdc-253c-41a7-841e-5edb3b56ce32",
                "942b6530-2407-420f-9c24-597adda6b2ce",
                "61cc1bc0-d4f5-4e2b-9152-79512045a4dd",
                "c049ff8b-3e5a-4cfb-bca6-e4a6cca9be28",
                "9a976b8e-72ba-468a-bea8-b37a31bb386b",
                "3c881f51-f75b-4959-834a-6e1d5edc32ae",
                "c91f0fe9-f2e9-4a17-84a5-8e4f2678ed3c",
                "2dfe8e4c-5bf6-43f1-93e1-6c320ede7226",
                "874049e7-629e-489a-b46c-1adf35ad40ee",
                "e0ca2fbc-7800-4b9b-afe5-8e42af9f5dd6",
            ]
        },
    },
    "slate": {
        "title": "Welcome to Volto!",
        "description": "The React powered content management system",
        "blocks": {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {"@type": "description"},
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "16f63011-a6ec-4f1c-8f78-4c5166dfff2c": {
                "@type": "slate",
                "plaintext": "You can log in and use it as admin user using these credentials :",
                "value": [
                    {
                        "children": [
                            {
                                "text": "You can log in and use it as admin user using these "
                            },
                            {"children": [{"text": "credentials"}], "type": "strong"},
                            {"text": ":"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "237b0f68-d700-47ec-9356-77a54c8d5237": {
                "@type": "slate",
                "plaintext": "Demo",
                "value": [{"children": [{"text": "Demo"}], "type": "h2"}],
            },
            "259ad2e9-a5f7-4e0c-a37b-b8d3a9da1a0d": {
                "@type": "slate",
                "plaintext": "password: admin ",
                "value": [
                    {
                        "children": [
                            {"text": "password: "},
                            {"children": [{"text": "admin"}], "type": "strong"},
                            {"text": ""},
                        ],
                        "type": "p",
                    }
                ],
            },
            "26d7d965-80f3-4312-9dc6-5166d00260a5": {
                "@type": "slate",
                "plaintext": "user: admin ",
                "value": [
                    {
                        "children": [
                            {"text": "user: "},
                            {"children": [{"text": "admin"}], "type": "strong"},
                            {"text": ""},
                        ],
                        "type": "p",
                    }
                ],
            },
            "38ff6b46-4cbd-4933-a462-251c3e963b7a": {
                "@type": "slate",
                "plaintext": " Plone is a CMS built on Python with over 21 years of experience. Plone has very interesting features that appeal to developers and users alike, such as customizable content types, hierarchical URL object traversing and a sophisticated content workflow powered by a granular permissions model. This allows you to build anything from simple websites to enterprise-grade intranets. Volto exposes all these features and communicates with Plone via its mature REST API . Volto can be esily themed and is highly customizable.",
                "value": [
                    {
                        "children": [
                            {"text": ""},
                            {
                                "children": [{"text": "Plone"}],
                                "data": {"url": "https://plone.org/"},
                                "type": "link",
                            },
                            {
                                "text": " is a CMS built on Python with over 21 years of experience. Plone has very interesting features that appeal to developers and users alike, such as customizable content types, hierarchical URL object traversing and a sophisticated content workflow powered by a granular permissions model. This allows you to build anything from simple websites to enterprise-grade intranets. Volto exposes all these features and communicates with Plone via its mature "
                            },
                            {
                                "children": [{"text": "REST API"}],
                                "data": {
                                    "url": "https://github.com/plone/plone.restapi"
                                },
                                "type": "link",
                            },
                            {
                                "text": ". Volto can be esily themed and is highly customizable."
                            },
                        ],
                        "type": "p",
                    }
                ],
            },
            "58cb10e2-49a5-4a87-9f5b-479c34bc5d36": {
                "@type": "slate",
                "plaintext": "You can use this site to test Volto. It runs on the master branch of Volto using latest Plone 5.2 Backend running on Python 3.",
                "value": [
                    {
                        "children": [
                            {
                                "text": "You can use this site to test Volto. It runs on the master branch of Volto using latest Plone 5.2 Backend running on Python 3."
                            }
                        ],
                        "type": "p",
                    }
                ],
            },
            "59f1e88e-bc2b-4aeb-95e7-26e0850fec0f": {
                "@type": "slate",
                "plaintext": f"{datetime.now().year} - Volto Team - Plone Foundation",
                "value": [
                    {
                        "children": [
                            {
                                "text": f"{datetime.now().year} - Volto Team - Plone Foundation"
                            }
                        ],
                        "type": "p",
                    }
                ],
            },
            "712fb2c2-865e-4a21-bc74-b044a411deff": {
                "@type": "slate",
                "plaintext": "Volto also supports other APIs like Guillotina , a Python resource management system, inspired by Plone and using the same basic concepts like traversal, content types and permissions model.",
                "value": [
                    {
                        "children": [
                            {"text": "Volto also supports other APIs like "},
                            {
                                "children": [{"text": "Guillotina"}],
                                "data": {"url": "https://guillotina.io/"},
                                "type": "link",
                            },
                            {
                                "text": ", a Python resource management system, inspired by Plone and using the same basic concepts like traversal, content types and permissions model."
                            },
                        ],
                        "type": "p",
                    }
                ],
            },
            "78ff07d8-dc59-4af9-a669-1d551953ef34": {
                "@type": "slate",
                "plaintext": " Volto is a React-based frontend for content management systems, currently supporting three backend implementations: Plone, Guillotina and a NodeJS reference implementation.",
                "value": [
                    {
                        "children": [
                            {"text": ""},
                            {
                                "children": [{"text": "Volto"}],
                                "data": {"url": "https://github.com/plone/volto"},
                                "type": "link",
                            },
                            {
                                "text": " is a React-based frontend for content management systems, currently supporting three backend implementations: Plone, Guillotina and a NodeJS reference implementation."
                            },
                        ],
                        "type": "p",
                    }
                ],
            },
            "ddc9926a-03d3-4c64-87a1-2b941aa08ebe": {
                "@type": "slate",
                "plaintext": "Happy hacking!",
                "value": [{"children": [{"text": "Happy hacking!"}], "type": "p"}],
            },
            "fe6a8835-78d6-4026-ac2e-55ed26de14c3": {
                "@type": "slate",
                "plaintext": " Disclaimer : This instance is reset every night, so all changes will be lost afterwards.",
                "value": [
                    {
                        "children": [
                            {"text": ""},
                            {"children": [{"text": "Disclaimer"}], "type": "strong"},
                            {
                                "text": ": This instance is reset every night, so all changes will be lost afterwards."
                            },
                        ],
                        "type": "p",
                    }
                ],
            },
        },
        "blocks_layout": {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19",
                "78ff07d8-dc59-4af9-a669-1d551953ef34",
                "38ff6b46-4cbd-4933-a462-251c3e963b7a",
                "712fb2c2-865e-4a21-bc74-b044a411deff",
                "237b0f68-d700-47ec-9356-77a54c8d5237",
                "58cb10e2-49a5-4a87-9f5b-479c34bc5d36",
                "16f63011-a6ec-4f1c-8f78-4c5166dfff2c",
                "26d7d965-80f3-4312-9dc6-5166d00260a5",
                "259ad2e9-a5f7-4e0c-a37b-b8d3a9da1a0d",
                "fe6a8835-78d6-4026-ac2e-55ed26de14c3",
                "ddc9926a-03d3-4c64-87a1-2b941aa08ebe",
                "59f1e88e-bc2b-4aeb-95e7-26e0850fec0f",
            ]
        },
    },
}


default_lrf_home = {
    "draftJS": {
        "blocks": {
            "15068807-cfc9-444a-97db-8c736809ff52": {"@type": "title"},
            "59d41d8a-ef05-4e21-8820-2a64f5878092": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "key": "618bl",
                            "text": "Nulla porttitor accumsan tincidunt. Sed porttitor lectus nibh. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Nulla porttitor accumsan tincidunt. Nulla porttitor accumsan tincidunt. Nulla porttitor accumsan tincidunt. Quisque velit nisi, pretium ut lacinia in, elementum id enim. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Sed porttitor lectus nibh. Pellentesque in ipsum id orci porta dapibus.",
                            "type": "unstyled",
                            "depth": 0,
                            "inlineStyleRanges": [],
                            "entityRanges": [],
                            "data": {},
                        }
                    ],
                    "entityMap": {},
                },
            },
        },
        "blocks_layout": {
            "items": [
                "15068807-cfc9-444a-97db-8c736809ff52",
                "59d41d8a-ef05-4e21-8820-2a64f5878092",
            ]
        },
    },
    "slate": {
        "blocks": {
            "15068807-cfc9-444a-97db-8c736809ff52": {"@type": "title"},
            "59d41d8a-ef05-4e21-8820-2a64f5878092": {
                "@type": "slate",
                "value": [
                    {
                        "type": "p",
                        "children": [
                            {
                                "text": "Nulla porttitor accumsan tincidunt. Sed porttitor lectus nibh. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Nulla porttitor accumsan tincidunt. Nulla porttitor accumsan tincidunt. Nulla porttitor accumsan tincidunt. Quisque velit nisi, pretium ut lacinia in, elementum id enim. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Sed porttitor lectus nibh. Pellentesque in ipsum id orci porta dapibus."
                            }
                        ],
                    }
                ],
                "plaintext": "Nulla porttitor accumsan tincidunt. Sed porttitor lectus nibh. Praesent sapien massa, convallis a pellentesque nec, egestas non nisi. Nulla porttitor accumsan tincidunt. Nulla porttitor accumsan tincidunt. Nulla porttitor accumsan tincidunt. Quisque velit nisi, pretium ut lacinia in, elementum id enim. Vestibulum ac diam sit amet quam vehicula elementum sed sit amet dui. Sed porttitor lectus nibh. Pellentesque in ipsum id orci porta dapibus.",
            },
        },
        "blocks_layout": {
            "items": [
                "15068807-cfc9-444a-97db-8c736809ff52",
                "59d41d8a-ef05-4e21-8820-2a64f5878092",
            ]
        },
    },
}


def create_default_homepage_draftjs(context):
    create_default_homepage(context, block_type="draftJS")


def create_default_homepage(context, default_home=default_lrf_home, block_type="slate"):
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
            default_home = default_home[block_type]

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
                portal[lang].blocks = default_home["blocks"]
                portal[lang].blocks_layout = default_home["blocks_layout"]

    else:
        create_root_homepage(context, block_type)


def create_root_homepage(context, block_type, default_home=default_home):
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
        default_home = default_home[block_type]

    logger.info(
        f"Creating default homepage in Plone {'6' if PLONE_6 else ''} site root with {block_type} blocks - not PAM enabled"
    )

    if PLONE_6:
        portal.blocks = default_home["blocks"]
        portal.blocks_layout = default_home["blocks_layout"]
        portal.title = default_home["title"]
        portal.description = default_home["description"]
    else:
        blocks = default_home["blocks"]
        blocks_layout = default_home["blocks_layout"]
        portal.setTitle(default_home["title"])
        portal.setDescription(default_home["description"])

        # Use the hack for setting the home page in Plone Site object
        if not getattr(portal, "blocks", False):
            portal.manage_addProperty("blocks", json.dumps(blocks), "string")

        if not getattr(portal, "blocks_layout", False):
            portal.manage_addProperty(
                "blocks_layout", json.dumps(blocks_layout), "string"
            )  # noqa


def create_demo_homepage(context):
    demo_home_page = {
        "title": "Welcome to Plone 6!",
        "description": "Congratulations! You have successfully installed Plone.",
        "blocks": {
            "0358abe2-b4f1-463d-a279-a63ea80daf19": {"@type": "description"},
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "2dfe8e4c-5bf6-43f1-93e1-6c320ede7226": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 10, "offset": 0, "style": "BOLD"}
                            ],
                            "key": "6470b",
                            "text": "Disclaimer: This instance is reset every night, so all changes will be lost afterwards.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "3c881f51-f75b-4959-834a-6e1d5edc32ae": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 5, "offset": 6, "style": "BOLD"}
                            ],
                            "key": "ekn3l",
                            "text": "user: admin",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "5e1c30b1-ec6c-4dc0-9483-9768c3c416e4": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "behki",
                            "text": "Plone is a powerful content management system built on a rock-solid application stack written using the Python programming language. More about these technologies:",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "5f7e6846-e27c-48c4-8c9a-f0d93eadb185": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "75pke",
                            "text": "\u2026protects and promotes Plone.",
                            "type": "unordered-list-item",
                        },
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "2mo73",
                            "text": "\u2026is a registered 501(c)(3) charitable organization.",
                            "type": "unordered-list-item",
                        },
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "9qhkg",
                            "text": "\u2026donations are tax-deductible.",
                            "type": "unordered-list-item",
                        },
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 50, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "5528b",
                            "text": "Support the Foundation and help make Plone better!",
                            "type": "unordered-list-item",
                        },
                    ],
                    "entityMap": {
                        "0": {
                            "data": {"url": "https://plone.org/sponsors/be-a-hero"},
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
            "61cc1bc0-d4f5-4e2b-9152-79512045a4dd": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "9qsa4",
                            "text": "Demo",
                            "type": "header-two",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "874049e7-629e-489a-b46c-1adf35ad40ee": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "9pnjr",
                            "text": "Happy hacking!",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "8bba235c-7a52-4ce2-bde1-c505e5746dce": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "692gs",
                            "text": "Plone is made possible only through the efforts of thousands of dedicated individuals and hundreds of companies. The Plone Foundation:",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "942b6530-2407-420f-9c24-597adda6b2ce": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "6a248",
                            "text": "Support the Plone Foundation",
                            "type": "header-two",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "9a976b8e-72ba-468a-bea8-b37a31bb386b": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 12, "offset": 51, "style": "BOLD"}
                            ],
                            "key": "94arl",
                            "text": "You can log in and use it as admin user using these credentials:",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "b3717238-448f-406e-b06f-57a9715c3326": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "1bnna",
                            "text": "Find out more about Plone",
                            "type": "header-two",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "c049ff8b-3e5a-4cfb-bca6-e4a6cca9be28": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "55n44",
                            "text": "You can use this site to test Plone 6. These are the versions used in this demo:",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "c91f0fe9-f2e9-4a17-84a5-8e4f2678ed3c": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [
                                {"length": 5, "offset": 10, "style": "BOLD"}
                            ],
                            "key": "buncq",
                            "text": "password: admin",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "e0ca2fbc-7800-4b9b-afe5-8e42af9f5dd6": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "f0prj",
                            "text": f"{datetime.now().year} - Plone Foundation",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 43, "offset": 4}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "The Plone open source Content Management System web site for evaluators and decision makers.",
                            "type": "unordered-list-item",
                        },
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 1, "length": 16, "offset": 4}],
                            "inlineStyleRanges": [],
                            "key": "4ec08",
                            "text": "The Plone community web site for developers.",
                            "type": "unordered-list-item",
                        },
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 2, "length": 27, "offset": 4}],
                            "inlineStyleRanges": [],
                            "key": "4q5m2",
                            "text": "The Python programming language web site.",
                            "type": "unordered-list-item",
                        },
                    ],
                    "entityMap": {
                        "0": {
                            "data": {"url": "https://plone.com/"},
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        },
                        "1": {
                            "data": {"url": "https://plone.org/"},
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        },
                        "2": {
                            "data": {"url": "https://www.python.org/"},
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        },
                    },
                },
            },
            "3b5ac7a5-2d98-423e-807c-5eebc0bf0054": {"@type": "system"},
        },
        "blocks_layout": {
            "items": [
                "07c273fc-8bfc-4e7d-a327-d513e5a945bb",
                "0358abe2-b4f1-463d-a279-a63ea80daf19",
                "b3717238-448f-406e-b06f-57a9715c3326",
                "5e1c30b1-ec6c-4dc0-9483-9768c3c416e4",
                "effbdcdc-253c-41a7-841e-5edb3b56ce32",
                "942b6530-2407-420f-9c24-597adda6b2ce",
                "8bba235c-7a52-4ce2-bde1-c505e5746dce",
                "5f7e6846-e27c-48c4-8c9a-f0d93eadb185",
                "61cc1bc0-d4f5-4e2b-9152-79512045a4dd",
                "c049ff8b-3e5a-4cfb-bca6-e4a6cca9be28",
                "3b5ac7a5-2d98-423e-807c-5eebc0bf0054",
                "9a976b8e-72ba-468a-bea8-b37a31bb386b",
                "3c881f51-f75b-4959-834a-6e1d5edc32ae",
                "c91f0fe9-f2e9-4a17-84a5-8e4f2678ed3c",
                "2dfe8e4c-5bf6-43f1-93e1-6c320ede7226",
                "874049e7-629e-489a-b46c-1adf35ad40ee",
                "e0ca2fbc-7800-4b9b-afe5-8e42af9f5dd6",
            ]
        },
    }

    create_root_homepage(context, default_home=demo_home_page)
