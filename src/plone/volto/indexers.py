from Acquisition import aq_base
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from plone.volto.behaviors.preview import IPreview


@indexer(IPreview)
def hasPreviewImage(obj):
    """
    Indexer for knowing in a catalog search if a content with the IPreview behavior has
    a preview_image
    """
    if obj.aq_base.preview_image:
        return True
    return False


@indexer(IDexterityContent)
def image_field_indexer(obj):
    """Indexer for knowing in a catalog search if a content has any image."""
    base_obj = aq_base(obj)

    image_field = ""
    if getattr(base_obj, "preview_image", False):
        image_field = "preview_image"
    elif getattr(base_obj, "image", False):
        image_field = "image"
    return image_field
