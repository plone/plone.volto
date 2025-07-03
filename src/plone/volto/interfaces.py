"""Module where all interfaces, events and exceptions live."""

from plone.volto import _
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
        title=_("Frontend domain"),
        description=_("Used for rewriting URLs sent in the password reset email by Plone."),
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
