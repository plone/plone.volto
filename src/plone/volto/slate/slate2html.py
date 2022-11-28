""" slate2html module """
# pylint: disable=import-error,no-name-in-module,too-few-public-methods,
# pylint: disable=not-callable,no-self-use,unused-argument,invalid-name
import json

from lxml.html import builder as E
from lxml.html import tostring

from .config import KNOWN_BLOCK_TYPES


def join(element, children):
    """join.

    :param element:
    :param children:
    """
    res = []
    for bit in children:
        res.append(bit)
        res.append(element)
    return res[:-1]  # remove the last break


class Slate2HTML(object):
    """Slate2HTML."""

    def serialize(self, element):
        """serialize.

        :param element:
        """
        if "text" in element:
            if "\n" not in element["text"]:
                return [element["text"]]

            return join(E.BR, element["text"].split("\n"))

        tagname = element["type"]

        if element.get("data") and element["type"] not in KNOWN_BLOCK_TYPES:
            handler = self.handle_slate_data_element
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
            if not handler and tagname in KNOWN_BLOCK_TYPES:
                handler = self.handle_block

        res = handler(element)
        if isinstance(res, list):
            return res
        return [res]

    def handle_tag_a(self, element):
        """handle_tag_a.

        :param element:
        """
        internal_link = (
            element.get("data", {})
            .get("link", {})
            .get("internal", {})
            .get("internal_link", [])
        )

        attributes = {}

        if internal_link:
            attributes["href"] = internal_link[0]["@id"]

        el = getattr(E, element["type"].upper())

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        return el(*children, **attributes)

    def handle_slate_data_element(self, element):
        """handle_slate_data_element.

        :param element:
        """
        el = E.SPAN

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        data = {"type": element["type"], "data": element["data"]}
        attributes = {"data-slate-data": json.dumps(data)}

        return el(*children, **attributes)

    def handle_block(self, element):
        """handle_block.

        :param element:
        """
        el = getattr(E, element["type"].upper())

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        return el(*children)

    def to_html(self, value):
        """to_html.

        :param value:
        """
        children = []
        for child in value:
            children += self.serialize(child)

        # TO DO: handle unicode properly
        return u"".join(tostring(f).decode("utf-8") for f in children)


def slate_to_html(value):
    """slate_to_html.

    :param value:
    """
    convert = Slate2HTML()
    return convert.to_html(value)
