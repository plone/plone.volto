from Acquisition import aq_base
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from plone.restapi.blocks import visit_blocks
from plone.volto.behaviors.preview import IPreview


@indexer(IPreview)
def hasPreviewImage(obj):
    """
    Indexer for knowing in a catalog search if a content with the IPreview behavior has
    a preview_image
    """
    if obj.aq_base.preview_image or (
        obj.aq_base.preview_image_link and not obj.preview_image_link.isBroken()
    ):
        return True
    return False


@indexer(IDexterityContent)
def image_field_indexer(obj):
    """Indexer for knowing in a catalog search if a content has any image."""
    base_obj = aq_base(obj)

    image_field = ""
    if (
        getattr(base_obj, "preview_image_link", False)
        and not base_obj.preview_image_link.isBroken()
    ):
        image_field = "preview_image_link"
    elif getattr(base_obj, "preview_image", False):
        image_field = "preview_image"
    elif getattr(base_obj, "image", False):
        image_field = "image"
    return image_field


@indexer(IDexterityContent)
def block_types_indexer(obj):
    """Indexer for all block types included in a page."""
    obj = aq_base(obj)
    block_types = set()
    for block in visit_blocks(obj, obj.blocks):
        block_type = block.get("@type")
        if block_type:
            block_types.add(block_type)
    return block_types
