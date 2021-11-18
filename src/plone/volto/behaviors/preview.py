# -*- coding: utf-8 -*-
from plone.volto import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IPreview(model.Schema):

    preview_image = namedfile.NamedBlobImage(
        title=_(u"label_previewimage", default=u"Preview image"),
        description=_(
            u"help_previewimage",
            default=u"Insert an image that will be used in listing and teaser blocks.",
        ),
        required=False,
    )

    preview_caption = TextLine(
        title=_(u"Preview image caption"), description=u"", required=False
    )
