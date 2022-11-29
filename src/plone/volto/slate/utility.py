""" utilities module """
from .html2slate import text_to_slate
from .slate2html import slate_to_html


class SlateConverter(object):
    """SlateConverter."""

    def html2slate(self, text):
        """html2slate.

        :param text:
        """
        value = text_to_slate(text)

        if not value:  # minimal proper value for slate
            return [{"type": "p", "children": [{"text": ""}]}]

        return value

    def slate2html(self, value):
        """slate2html.

        :param value:
        """
        return slate_to_html(value)
