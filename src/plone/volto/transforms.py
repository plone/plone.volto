from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import ResolveUIDDeserializerBase
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import ResolveUIDSerializerBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


class NestedResolveUIDDeserializerBase(object):
    """The "url" smart block field for nested blocks

    This is a generic handler. In all blocks, it converts any "url"
    field from using resolveuid to an "absolute" URL
    """

    order = 1
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _transform(self, block):
        """this mutates the object directly"""

        block_type = block.get("@type", "")
        handlers = []
        for h in subscribers(
            (self.context, self.request), IBlockFieldDeserializationTransformer
        ):
            if h.block_type == block_type or h.block_type is None:
                h.blockid = block.get("id", None)
                handlers.append(h)

        for handler in sorted(handlers, key=lambda h: h.order):
            block = handler(block)

        return block

    def __call__(self, block):
        for nested_name in ["columns", "hrefList", "slides"]:
            nested_blocks = block.get(nested_name, [])
            if not isinstance(nested_blocks, list):
                continue
            for nested_block in nested_blocks:
                self._transform(nested_block)
        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDDeserializer(NestedResolveUIDDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDDeserializerRoot(NestedResolveUIDDeserializerBase):
    """Deserializer for site root"""


class NestedResolveUIDSerializerBase(object):
    order = 1
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _transform(self, block):
        """this mutates the object directly"""

        block_type = block.get("@type", "")
        handlers = []
        for h in subscribers(
            (self.context, self.request), IBlockFieldSerializationTransformer
        ):
            if h.block_type == block_type or h.block_type is None:
                h.blockid = block.get("id", None)
                handlers.append(h)

        for handler in sorted(handlers, key=lambda h: h.order):
            block = handler(block)

        return block

    def __call__(self, block):
        for nested_name in ["columns", "hrefList", "slides"]:
            nested_blocks = block.get(nested_name, [])
            if not isinstance(nested_blocks, list):
                continue
            for nested_block in nested_blocks:
                self._transform(nested_block)
        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDSerializer(NestedResolveUIDSerializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDSerializerRoot(NestedResolveUIDSerializerBase):
    """Deserializer for site root"""


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
