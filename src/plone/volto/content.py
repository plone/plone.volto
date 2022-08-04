# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.interfaces import INewsItem
from plone.dexterity.content import Container
from plone.volto.interfaces import IFolderishDocument
from plone.volto.interfaces import IFolderishEvent
from plone.volto.interfaces import IFolderishNewsItem
from zope.interface import implementer


@implementer(IDocument, IFolderishDocument)
class FolderishDocument(Container):
    pass


@implementer(IEvent, IFolderishEvent)
class FolderishEvent(Container):
    pass


@implementer(INewsItem, IFolderishNewsItem)
class FolderishNewsItem(Container):
    pass
