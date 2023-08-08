""" Transformers to store the slate HTML value serialized as HTML
"""

from .interfaces import ISlateConverter
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import logging


logger = logging.getLogger("slate")


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateHTMLBlockSerializer(object):
    """Serialize the content of an HTML block as Slate value"""

    field = "value"
    order = -1000  # should be the first
    block_type = "slate"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):

        if not block:
            block = {}

        value = block.get(self.field, "")

        if isinstance(value, str):
            block["value"] = getUtility(ISlateConverter).html2slate(value)
            logger.info("Converted to slate: %s ===> %s", value, block["value"])
            return block

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateHTMLBlockSerializerRoot(SlateHTMLBlockSerializer):
    """Serializer for site root"""


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateHTMLBlockDeserializer(object):
    """Store a slate value as an HTML"""

    field = "value"
    order = 1000  # needs to be the last
    block_type = "slate"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        if not block:
            block = {}

        value = block.get(self.field, [])
        block["value"] = getUtility(ISlateConverter).slate2html(value)
        logger.info("Converted to html %s ====> %s", value, block["value"])
        return block


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateHTMLBlockDeserializerRoot(SlateHTMLBlockDeserializer):
    """Deserializer for site root"""
