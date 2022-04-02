# -*- coding: utf-8 -*-

from plone import api
from plone.stringinterp.adapters import BaseSubstitution
from plone.volto import _
from Products.CMFCore.interfaces import IContentish
from zope.component import adapter


@adapter(IContentish)
class VoltoAbsoluteURLSubstitution(BaseSubstitution):
    """URL Substitution adapter"""

    category = _("All Content")
    description = _("Volto URL")

    def safe_call(self):
        """get the url"""
        context_url = self.context.absolute_url()
        plone_domain = api.portal.get().absolute_url()
        frontend_domain = api.portal.get_registry_record("volto.frontend_domain")
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]

        return context_url.replace(plone_domain, frontend_domain)
