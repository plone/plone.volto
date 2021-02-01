from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.serializer.blocks import uid_to_url
from Products.CMFPlone.interfaces import IPloneSiteRoot
from six import string_types
from zope.component import adapter
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

    def __call__(self, block):
        for column_name in ["columns", "hrefList"]:
            column_field = block.get(column_name, [])
            if block.get(column_name, False):
                for index, item in enumerate(column_field):
                    for field in ["url", "href"]:
                        link = item.get(field, "")
                        if link and isinstance(link, string_types):
                            block[column_name][index][field] = path2uid(
                                context=self.context, link=link
                            )
                        elif link and isinstance(link, list):
                            block[column_name][index][field] = [
                                path2uid(context=self.context, link=linkitem)
                                for linkitem in link
                            ]
        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDDeserializer(NestedResolveUIDDeserializerBase):
    """ Deserializer for content-types that implements IBlocks behavior """


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDDeserializerRoot(NestedResolveUIDDeserializerBase):
    """ Deserializer for site root """


class NestedResolveUIDSerializerBase(object):
    order = 1
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        for column_name in ["columns", "hrefList"]:
            column_field = value.get(column_name, [])
            if value.get(column_name, False):
                for index, item in enumerate(column_field):
                    for field in ["url", "href"]:
                        if field in item.keys():
                            link = item.get(field, "")
                            if isinstance(link, string_types):
                                value[column_name][index][field] = uid_to_url(link)
                            elif isinstance(link, list):
                                value[column_name][index][field] = [
                                    uid_to_url(linkitem) for linkitem in link
                                ]

        return value


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDSerializer(NestedResolveUIDSerializerBase):
    """ Deserializer for content-types that implements IBlocks behavior """


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class NestedResolveUIDSerializerRoot(NestedResolveUIDSerializerBase):
    """ Deserializer for site root """
