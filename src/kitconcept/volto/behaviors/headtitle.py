# -*- coding: utf-8 -*-
from fzj.internet import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider
from zope import schema


@provider(IFormFieldProvider)
class IHeadTitle(model.Schema):

    headtitle = schema.TextLine(
        title=_("Header title"),
        required=False,
        description=_("Header title should consist of year and number of the report"),
    )
