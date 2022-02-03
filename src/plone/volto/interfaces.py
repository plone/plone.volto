# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPloneVoltoCoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IThemeSpecific(IPloneVoltoCoreLayer):
    """bbb for collective.folderishtypes browser interface."""


class IVoltoSettings(Interface):
    """Volto settings necessary to store in the backend"""

    frontend_domain = schema.URI(
        title="Frontend domain",
        description="Used for rewriting URL's sent in the password reset e-mail by Plone.",
        default="http://localhost:3000",
    )


class IFolderishType(Interface):
    """Marker interface"""


class IFolderishDocument(IFolderishType):
    """Marker interface"""


class IFolderishEvent(IFolderishType):
    """Marker interface"""


class IFolderishNewsItem(IFolderishType):
    """Marker interface"""
