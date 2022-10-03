# -*- coding: utf-8 -*-
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from plone.volto import _
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IPreview(model.Schema):

    preview_image = namedfile.NamedBlobImage(
        title=_("label_previewimage", default="Preview image"),
        description=_(
            "help_previewimage",
            default="Insert an image that will be used in listing and teaser blocks.",
        ),
        required=False,
    )

    preview_caption = TextLine(
        title=_("Preview image caption"), description="", required=False
    )
