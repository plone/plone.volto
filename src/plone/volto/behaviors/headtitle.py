# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.volto import _
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IHeadTitle(model.Schema):

    head_title = schema.TextLine(
        title=_("label_head_title", default="Header title"),
        required=False,
        description=_(
            "help_head_title",
            default="The header title is shown above the title in teasers.",
        ),
    )
