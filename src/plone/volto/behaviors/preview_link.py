# -*- coding: utf-8 -*-
from plone.volto import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives
from plone.supermodel import model
from zope.interface import provider
from zope.schema import TextLine
from z3c.relationfield.schema import RelationChoice
from plone.app.z3cform.widget import RelatedItemsFieldWidget


@provider(IFormFieldProvider)
class IPreviewLink(model.Schema):

    preview_image_link = RelationChoice(
        title=_("label_previewimage", default="Preview image"),
        description=_(
            "help_previewimage",
            default="Insert an image that will be used in listing and teaser blocks.",
        ),
        vocabulary='plone.app.vocabularies.Catalog',
        required=False,
    )

    directives.widget(
        'preview_image_link',
        RelatedItemsFieldWidget,
        pattern_options={
            'selectableTypes': ['Image'],
        },
        frontendOptions={
          "widgetProps": {"return": "single"},
        },
    )

    preview_caption_link = TextLine(
        title=_("Preview image caption"), description="", required=False
    )
