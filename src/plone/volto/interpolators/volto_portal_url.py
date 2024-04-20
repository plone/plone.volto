# -*- coding: utf-8 -*-

from plone import api
from plone.stringinterp.adapters import BaseSubstitution
from plone.volto import _
from Products.CMFCore.interfaces import IContentish
from zope.component import adapter


@adapter(IContentish)
class VoltoPortalURLSubstitution(BaseSubstitution):
    """URL Substitution adapter"""

    category = _("All Content")
    description = _("Volto Portal URL")

    def safe_call(self):
        """get the url"""
        frontend_domain = api.portal.get_registry_record("volto.frontend_domain")
        return frontend_domain
