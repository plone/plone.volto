"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface


class ISlateNodeSerializeTransform(Interface):
    """Transformers for slate nodes serialization (publish to frontend)"""


class ISlateNodeDeserializeTransform(Interface):
    """Transformer on slate nodes deserialization (save to backend)"""


class ISlateConverter(Interface):
    """A convertor utility"""

    def html2slate():
        """Convert HTML to slate value"""

    def slate2html():
        """Convert Slate value to slate HTML"""
