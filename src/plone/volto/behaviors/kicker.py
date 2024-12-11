from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.volto import _
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class IKicker(model.Schema):

    # The field itself is named head_title, for backwards-compatibility.
    head_title = schema.TextLine(
        title=_("label_kicker", default="Kicker"),
        required=False,
        description=_(
            "help_kicker",
            default="The kicker is a line of text shown above the title.",
        ),
    )


@provider(IFormFieldProvider)
class IHeadTitle(IKicker):
    """alias for backwards-compatibility"""
