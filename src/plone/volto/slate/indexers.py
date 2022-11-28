""" indexers module """
# pylint: disable=too-few-public-methods


class SlateTextIndexer(object):
    """SlateTextIndexer."""

    def __init__(self, context, request):
        """__init__.

        :param context:
        :param request:
        """
        self.context = context
        self.request = request

    def __call__(self, block):
        """__call__.

        :param block:
        """
        # text indexer for slate blocks. Relies on the slate field
        block = block or {}

        if block.get("searchableText"):
            return None

        # BBB compatibility with slate blocks that used the "plaintext" field
        return (block or {}).get("plaintext", "")
