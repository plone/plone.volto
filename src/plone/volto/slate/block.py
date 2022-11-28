# pylint: disable=import-error,no-name-in-module,too-few-public-methods,
# pylint: disable=not-callable,no-self-use,unused-argument
""" block module """
import os

from zope.interface import implementer
from zope.component import adapter
from zope.publisher.interfaces.browser import IBrowserRequest
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.interfaces import (IBlockFieldDeserializationTransformer,
                                      IBlockFieldSerializationTransformer)
from plone.restapi.serializer.blocks import uid_to_url
from Products.CMFPlone.interfaces import IPloneSiteRoot

from .utils import iterate_children


def transform_links(context, value, transformer):
    """ Convert absolute links to resolveuid
       http://localhost:55001/plone/link-target
       ->
       ../resolveuid/023c61b44e194652804d05a15dc126f4"""
    data = value.get("data", {})
    if data.get("link", {}).get("internal", {}).get("internal_link"):
        internal_link = data["link"]["internal"]["internal_link"]
        for link in internal_link:
            link["@id"] = transformer(context, link["@id"])


class SlateBlockTransformer(object):
    """SlateBlockTransformer."""

    field = "value"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # if isinstance(block["value"], six.string_types):
        #     import pdb
        #
        #     pdb.set_trace()

        value = getattr(block, self.field, [])
        for child in iterate_children(value or []):
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, "handle_{}".format(node_type), None)
                if handler:
                    handler(child)

        return block


class SlateBlockSerializerBase(SlateBlockTransformer):
    """SlateBlockSerializerBase."""

    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def _uid_to_url(self, context, path):
        """_uid_to_url.

        :param context:
        :param path:
        """
        portal = api.portal.get()
        return uid_to_url(path).replace(portal.absolute_url(), "")

    def handle_a(self, child):
        """handle_a.

        :param child:
        """
        transform_links(self.context, child, transformer=self._uid_to_url)


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """ Serializer for content-types with IBlocks behavior """


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateBlockSerializerRoot(SlateBlockSerializerBase):
    """ Serializer for site root """


class SlateBlockDeserializerBase(SlateBlockTransformer):
    """SlateBlockDeserializerBase."""

    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def handle_a(self, child):
        """handle_a.

        :param child:
        """
        transform_links(self.context, child, transformer=path2uid)


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializer(SlateBlockDeserializerBase):
    """ Deserializer for content-types that implements IBlocks behavior """


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializerRoot(SlateBlockDeserializerBase):
    """ Deserializer for site root """
