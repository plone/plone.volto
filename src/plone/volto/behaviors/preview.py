# -*- coding: utf-8 -*-
from plone.volto import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.interface import provider
from zope.schema import TextLine
from plone.supermodel.directives import primary


@provider(IFormFieldProvider)
class IPreview(model.Schema):

    model.fieldset(
        "preview_fields",
        label=_(u"Preview Fields"),
        fields=["nav_title", "preview_image", "preview_caption"],
    )
    primary("nav_title")

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
    nav_title = TextLine(title=_("Navigation title"), required=False)
