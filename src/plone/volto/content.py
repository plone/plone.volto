# -*- coding: utf-8 -*-
from collective.folderishtypes.interfaces import IFolderishDocument
from collective.folderishtypes.interfaces import IFolderishEvent
from collective.folderishtypes.interfaces import IFolderishNewsItem
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IEvent
from plone.app.contenttypes.interfaces import INewsItem
from plone.dexterity.content import Container
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
