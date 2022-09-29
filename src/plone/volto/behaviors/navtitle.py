# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.volto import _
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class INavTitle(model.Schema):

    nav_title = TextLine(title=_("Navigation title"), required=False)
