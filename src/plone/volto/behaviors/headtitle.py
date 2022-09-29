# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.volto import _
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IHeadTitle(model.Schema):

    head_title = schema.TextLine(
        title=_("Header title"),
        required=False,
        description=_("Header title should consist of year and number of the report"),
    )
