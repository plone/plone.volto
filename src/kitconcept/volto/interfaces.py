# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IKitconceptvoltoCoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IVoltoSettings(Interface):
    """ Volto settings necessary to store ont he backend
    """

    frontend_domain = schema.URI(
        title="Frontend domain",
        description="Used for rewriting URL's sent in the password reset e-mail by Plone.",
        default="http://localhost:3000",
    )
