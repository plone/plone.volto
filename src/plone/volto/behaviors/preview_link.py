from plone import api
from plone.app.contenttypes.interfaces import IImage
from plone.app.z3cform.widgets.relateditems import RelatedItemsFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.base.interfaces import IImageScalesFieldAdapter
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.supermodel import model
from plone.volto import _
from z3c.form.util import getSpecification
from z3c.relationfield.schema import RelationChoice
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema import TextLine


# Allow choosing preview images from a different language tree in a multi-lingual site.
# See https://github.com/plone/plone.volto/issues/172
try:
    import plone.app.multilingual  # noqa

    VOCAB = "plone.app.multilingual.RootCatalog"
except ImportError:
    VOCAB = "plone.app.vocabularies.Catalog"


@provider(IFormFieldProvider)
class IPreviewLink(model.Schema):

    model.fieldset(
        "preview_image",
        _("label_previewimage", default="Preview image"),
        fields=["preview_image_link", "preview_caption_link"],
    )

    preview_image_link = RelationChoice(
        title=_("label_previewimage", default="Preview image"),
        description=_(
            "help_previewimage",
            default="Select an image that will be used in listing and teaser blocks.",
        ),
        vocabulary=VOCAB,
        required=False,
    )

    directives.widget(
        "preview_image_link",
        RelatedItemsFieldWidget,
        frontendOptions={
            "widget": "object_browser",
            "widgetProps": {"mode": "image", "return": "single"},
        },
    )

    preview_caption_link = TextLine(
        title=_("Preview image caption"), description="", required=False
    )


@adapter(getSpecification(IPreviewLink["preview_image_link"]), Interface, Interface)
@implementer(IImageScalesFieldAdapter)
class PreviewImageScalesFieldAdapter:
    """Get the image_scales for the preview_image_link field"""

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __call__(self):
        value = self.field.get(self.context)
        if value:
            linked_image = value.to_object
            primary_field = IPrimaryFieldInfo(linked_image).field
            serializer = queryMultiAdapter(
                (primary_field, linked_image, self.request), IImageScalesFieldAdapter
            )
            if serializer is not None:
                values = serializer()
                if values:
                    portal_url = api.portal.get().absolute_url()
                    base_path = linked_image.absolute_url().replace(portal_url, "")
                    for value in values:
                        value["base_path"] = base_path
                return values

        return []


@adapter(IImage, IObjectModifiedEvent)
def update_preview_image_scales(obj, event):
    """When an image is modified, update the image_scales metadata
    on other items that use it as a preview image.
    """
    for rel in api.relation.get(
        target=obj, relationship="preview_image_link", unrestricted=True
    ):
        rel.from_object.reindexObject(idxs=["image_scales"], update_metadata=True)
