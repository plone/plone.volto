# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'kitconcept.volto:uninstall',
        ]


def post_install(context):
    """Post install script"""


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def add_catalog_indexes(context, wanted=None):
    """Method to add our wanted indexes to the portal_catalog.
    """
    catalog = api.portal.get_tool('portal_catalog')
    indexes = catalog.indexes()
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
    if len(indexables) > 0:
        catalog.manage_reindexIndex(ids=indexables)
