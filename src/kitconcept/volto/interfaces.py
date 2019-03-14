# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from plone.supermodel import model


class IKitconceptvoltoCoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IHomepage(model.Schema):
    """Homepage content type interface."""
