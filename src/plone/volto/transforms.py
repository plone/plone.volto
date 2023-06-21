from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import ResolveUIDDeserializerBase
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IBlockVisitor
from plone.restapi.serializer.blocks import ResolveUIDSerializerBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IBlockVisitor)
@adapter(Interface, IBrowserRequest)
class NestedBlocksVisitor:
    """Visit nested blocks in columns, hrefList, or slides."""

    def __init__(self, context, request):
        pass

    def __call__(self, block_value):
        for nested_name in ("columns", "hrefList", "slides"):
            nested_blocks = block_value.get(nested_name, [])
            if not isinstance(nested_blocks, list):
                continue
            yield from nested_blocks


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class PreviewImageResolveUIDDeserializer(ResolveUIDDeserializerBase):
    """Deserializer for resolveuid in preview_image field"""

    fields = ["preview_image"]


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class PreviewImageResolveUIDDeserializerRoot(ResolveUIDDeserializerBase):
    """Deserializer for resolveuid in preview_image field on site root"""

    fields = ["preview_image"]


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldSerializationTransformer)
class PreviewImageResolveUIDSerializer(ResolveUIDSerializerBase):
    """Serializer for resolveuid in preview_image field"""

    fields = ["preview_image"]


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldSerializationTransformer)
class PreviewImageResolveUIDSerializerRoot(ResolveUIDSerializerBase):
    """Serializer for resolveuid in preview_image field on site root"""

    fields = ["preview_image"]
