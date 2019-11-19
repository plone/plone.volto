# -*- coding: utf-8 -*-
from kitconcept.volto import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class IPreview(model.Schema):

    preview_image = namedfile.NamedBlobImage(
        title=_(u"label_previewimage", default=u"Vorschaubild"),
        description=u"",
        required=False,
    )

    preview_caption = TextLine(
        title=_(u"Legende zum Vorschaubild"),
        description=_(u"Bitte Lizenzinformationen in folgender Form angeben"),
        required=False,
    )
