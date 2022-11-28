""" utilities module """
# pylint: disable=no-self-use
from .html2slate import text_to_slate
from .slate2html import slate_to_html


class SlateConverter(object):
    """SlateConverter."""

    def html2slate(self, text):
        """html2slate.

        :param text:
        """
        return text_to_slate(text)

    def slate2html(self, value):
        """slate2html.

        :param value:
        """
        return slate_to_html(value)
