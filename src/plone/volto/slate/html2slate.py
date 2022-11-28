""" Convert HTML to slate, slate to HTML

A port of volto-slate' deserialize.js module
"""

import json
import re
from collections import deque

from resiliparse.parse.html import HTMLTree

from .config import (DEFAULT_BLOCK_TYPE, ELEMENT_NODE, INLINE_ELEMENTS,
                     KNOWN_BLOCK_TYPES, TEXT_NODE)

SPACE_BEFORE_ENDLINE = re.compile(r"\s+\n", re.M)
SPACE_AFTER_DEADLINE = re.compile(r"\n\s+", re.M)
TAB = re.compile(r"\t", re.M)
LINEBREAK = re.compile(r"\n", re.M)
MULTIPLE_SPACE = re.compile(r" ( +)", re.M)
FIRST_SPACE = re.compile("^ ", re.M)
FIRST_ANY_SPACE = re.compile(r"^\s", re.M)
FIRST_ALL_SPACE = re.compile(r"^\s+", re.M)
ANY_SPACE_AT_END = re.compile(r"\s$", re.M)


def is_inline_slate(el):
    """Returns true if the element is a text node

    Some richtext editors provide support for "inline elements", which is to
    say they mark some portions of text and add flags for that, like
    "bold:true,italic:true", etc.

    From experience, this is a bad way to go when the output is intended to be
    HTML. In HTML DOM there is only markup and that markup is semantic. So
    keeping it purely markup greately simplifies the number of cases that need
    to be covered.
    """

    if isinstance(el, dict) and "text" in el:
        return True

    return False


def merge_adjacent_text_nodes(children):
    "Given a list of Slate elements, it combines adjacent texts nodes"

    ranges = []
    for i, v in enumerate(children):
        if "text" in v:
            if ranges and ranges[-1][1] == i - 1:
                ranges[-1][1] = i
            else:
                ranges.append([i, i])
    text_positions = []
    range_dict = {}
    for start, end in ranges:
        text_positions.extend(list(range(start, end + 1)))
        range_dict[start] = end

    result = []
    for i, v in enumerate(children):
        if i not in text_positions:
            result.append(v)
        if i in range_dict:
            result.append(
                {"text": "".join([c["text"] for c in children[i : range_dict[i] + 1]])}
            )
    return result


def remove_space_before_after_endline(text):
    text = SPACE_BEFORE_ENDLINE.sub("\n", text)
    text = SPACE_AFTER_DEADLINE.sub("\n", text)
    return text


def convert_tabs_to_spaces(text):
    return TAB.sub(" ", text)


def convert_linebreaks_to_spaces(text):
    return LINEBREAK.sub(" ", text)


def remove_space_follow_space(text, node):
    """Any space immediately following another space (even across two separate inline
    elements) is ignored (rule 4)
    """

    text = MULTIPLE_SPACE.sub(" ", text)

    if not text.startswith(" "):
        return text

    previous = node.prev
    if previous:
        if previous.type == TEXT_NODE:
            if previous.text.endswith(" "):
                return FIRST_SPACE.sub("", text)
        elif is_inline(previous):
            prev_text = collapse_inline_space(previous)
            if prev_text.endswith(" "):
                return FIRST_SPACE.sub("", text)
    else:
        parent = node.parent
        if parent.prev:
            prev_text = collapse_inline_space(parent.prev)
            if prev_text and prev_text.endswith(" "):
                return FIRST_SPACE.sub("", text)
        else:
            return FIRST_SPACE.sub("", text)

    return text


def is_inline(node):
    if isinstance(node, str) or node.type == TEXT_NODE:
        return True

    if node.tag.upper() in INLINE_ELEMENTS:
        return True

    return False


def remove_element_edges(text, node):
    previous = node.prev
    next_ = node.next
    parent = node.parent

    if (not is_inline(parent)) and (previous is None) and FIRST_ANY_SPACE.search(text):
        text = FIRST_ALL_SPACE.sub("", text)

    if ANY_SPACE_AT_END.search(text):
        if ((next_ is None) and (not is_inline(parent))) or (
            next_ and next_.tag == "br"
        ):
            text = ANY_SPACE_AT_END.sub("", text)

    return text


def clean_padding_text(text, node):
    """Cleans head/tail whitespaces of a single html text with multiple toplevel tags"""

    if is_whitespace(text):
        has_prev = node.prev and node.prev.type == ELEMENT_NODE
        has_next = node.next and node.next.type == ELEMENT_NODE

        if has_prev and has_next:
            return ""

        if node.prev and not node.next:
            return ""

        if node.next and not node.prev:
            return ""

    return text


def collapse_inline_space(node, expanded=False):
    """See

    https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Whitespace
    """
    text = node.text or ""

    # 0 (Volto). Return None if is text between block nodes
    text = clean_padding_text(text, node)

    # 1. all spaces and tabs immediately before and after a line break are ignored
    text = remove_space_before_after_endline(text)

    # 2. Next, all tab characters are handled as space characters
    text = convert_tabs_to_spaces(text)

    # 3. Convert all line breaks to spaces
    text = convert_linebreaks_to_spaces(text)

    # 4. Any space immediately following another space
    # (even across two separate inline elements) is ignored
    text = remove_space_follow_space(text, node)

    # 5. Sequences of spaces at the beginning and end of an element are removed
    text = remove_element_edges(text, node)

    return text


def fragments_fromstring(text):
    tree = HTMLTree.parse(text)
    document = tree.document
    body = document.query_selector("body")
    return body.child_nodes


class HTML2Slate(object):
    """A parser for HTML to slate conversion

    If you need to handle some custom slate markup, inherit and extend

    See https://github.com/plone/volto/blob/5f9066a70b9f3b60d462fc96a1aa7027ff9bbac0/packages/volto-slate/src/editor/deserialize.js
    """

    def to_slate(self, text):
        "Convert text to a slate value. A slate value is a list of elements"

        fragments = fragments_fromstring(text)
        nodes = []
        for f in fragments:
            slate_nodes = self.deserialize(f)
            if slate_nodes:
                nodes += slate_nodes

        return self.normalize(nodes)

    def deserialize(self, node):
        """Deserialize a node into a list Slate Nodes"""

        if node is None:
            return []

        if node.tag == "#text":
            text = collapse_inline_space(node)
            return [{"text": text}] if text else None
        elif node.type != ELEMENT_NODE:
            return None

        tagname = node.tag
        handler = None

        if "data-slate-data" in node.attrs:
            handler = self.handle_slate_data_element
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
            if not handler and tagname in KNOWN_BLOCK_TYPES:
                handler = self.handle_block

        if handler:
            slate_node = handler(node)
            if not isinstance(slate_node, list):
                slate_node = [slate_node]
            return slate_node

        # fallback, "skips" the node
        return self.handle_fallback(node)

    def deserialize_children(self, node):
        """deserialize_children.

        :param node:
        """

        res = []

        for child in node.child_nodes:
            b = self.deserialize(child)
            if isinstance(b, list):
                res += b
            elif b:
                res.append(b)

        return res

    def handle_tag_a(self, node):
        """handle_tag_a.

        :param node:
        """
        link = node["href"] if "href" in node.attrs else ""

        element = {"type": "a", "children": self.deserialize_children(node)}
        if link:
            if link.startswith("http") or link.startswith("//"):
                # TO DO: implement external link
                pass
            else:
                element["data"] = {
                    "link": {
                        "internal": {
                            "internal_link": [
                                {
                                    "@id": link,
                                }
                            ]
                        }
                    }
                }

        return element

    def handle_tag_br(self, node):
        """handle_tag_br.

        :param node:
        """
        return {"text": "\n"}

    def handle_block(self, node):
        """handle_block.

        :param node:
        """
        return {"type": node.tag, "children": self.deserialize_children(node)}

    def handle_tag_b(self, node):
        # TO DO: implement <b> special cases
        return self.handle_block(node)

    def handle_slate_data_element(self, node):
        """handle_slate_data_element.

        :param node:
        """
        element = json.loads(node["data-slate-data"])
        element["children"] = self.deserialize_children(node)
        return element

    def handle_fallback(self, node):
        """Unknown tags (for example span) are handled as pipe-through"""
        return self.deserialize_children(node)

    def normalize(self, value):
        """Normalize value to match Slate constraints"""

        assert isinstance(value, list)
        value = [v for v in value if v is not None]

        # all top-level elements in the value need to be block tags
        if value and [x for x in value if is_inline_slate(value[0])]:
            value = [{"type": DEFAULT_BLOCK_TYPE, "children": value}]

        stack = deque(value)

        while stack:
            child = stack.pop()
            children = child.get("children", None)
            if children is not None:
                children = [c for c in children if c]
                # merge adjacent text nodes
                child["children"] = merge_adjacent_text_nodes(children)
                stack.extend(child["children"])

                self._pad_with_space(child["children"])

        return value

    def _pad_with_space(self, children):
        """Mutate the children array in-place. It pads them with
        'empty spaces'.

        Extract from Slate docs:
        https://docs.slatejs.org/concepts/02-nodes#blocks-vs-inlines

        You can define which nodes are treated as inline nodes by overriding
        the editor.isInline function. (By default it always returns false.).
        Note that inline nodes cannot be the first or last child of a parent
        block, nor can it be next to another inline node in the children array.
        Slate will automatically space these with { text: '' } children by
        default with normalizeNode.

        Elements can either contain block elements or inline elements
        intermingled with text nodes as children. But elements cannot contain
        some children that are blocks and some that are inlines.
        """

        # TO DO: needs reimplementation according to above info
        if len(children) == 0:
            children.append({"text": ""})
            return

        if not children[0].get("text"):
            children.insert(0, {"text": ""})
        if not children[-1].get("text"):
            children.append({"text": ""})


def text_to_slate(text):
    """text_to_slate.

    :param text:
    """
    return HTML2Slate().to_slate(text)


def is_whitespace(text):
    """Returns true if the text is only whitespace characters"""

    # TODO: rewrite using mozila code

    if not isinstance(text, str):
        return False

    return len(re.sub(r"\s|\t|\n", "", text)) == 0
