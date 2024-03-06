# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.volto import _
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IKicker(model.Schema):

    kicker = schema.TextLine(
        title=_("label_kicker", default="Kicker"),
        required=False,
        description=_(
            "help_kicker",
            default="The kicker is shown above the title in teasers.",
        ),
    )


class IHeadTitle(IKicker):
    """alias for backwards-compatibility"""
