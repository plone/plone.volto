from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldLinkIntegrityRetriever
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class NestedBlockLinkRetriever:
    """Retrieve internal links from nested blocks.

    Handles the same keys as the resolveuid transform
    (columns, hrefList, and slides)
    """

    order = 2
    block_type = None  # any block type

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        links = set()
        for nested_name in ("columns", "hrefList", "slides"):
            nested_blocks = block.get(nested_name, [])
            if not isinstance(nested_blocks, list):
                continue
            for nested_block in nested_blocks:
                links |= self.retrieveLinks(nested_block)
        return links

    def retrieveLinks(self, block):
        links = set()
        block_type = block.get("@type", None)
        handlers = []
        for h in subscribers(
            (self.context, self.request),
            IBlockFieldLinkIntegrityRetriever,
        ):
            if h.block_type == block_type or h.block_type is None:
                handlers.append(h)
        for handler in sorted(handlers, key=lambda h: h.order):
            links |= set(handler(block))
        return links
