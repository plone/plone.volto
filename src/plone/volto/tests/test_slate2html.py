""" Slate2HTML module """
# pylint: disable=import-error,no-name-in-module,too-few-public-methods,
# pylint: disable=not-callable,no-self-use,unused-argument,invalid-name
# -*- coding: utf-8 -*-

import json
import os
import re
import unittest

from pkg_resources import resource_filename

# from eea.volto.slate.html2slate import text_to_slate
from eea.volto.slate.slate2html import slate_to_html


def read_data(filename):
    """read_data.

    :param filename:
    """
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data",
                                                              filename))

    with open(fpath) as f:
        return f.read()


def read_json(filename):
    """read_json.

    :param filename:
    """
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data",
                                                              filename))

    with open(fpath) as f:
        return json.load(f)


def clean_whitespace(html):
    """clean_whitespace.

    :param html:
    """
    html = html.replace("\n", " ")
    html = re.sub(r"\s+", " ", html)
    html = html.replace("> <", "><")
    return html


class TestConvertSlate2HTML(unittest.TestCase):
    """TestConvertSlate2HTML."""

    maxDiff = None

    def test_convert_simple_string(self):
        """test_convert_simple_string."""
        res = slate_to_html([{"children": [{"text": "Hello world"}],
                              "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")

    def test_convert_simple_paragraph(self):
        """test_convert_simple_paragraph."""
        res = slate_to_html([{"children": [{"text": "Hello world"}],
                              "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")

    def test_convert_simple_paragraph_multi_breaks(self):
        """test_convert_simple_paragraph_multi_breaks."""
        res = slate_to_html(
            [
                {
                    "children": [
                        {"text":
                         "Hello \nworld \n in a multi line \nparagraph"}
                    ],
                    "type": "p",
                }
            ]
        )
        self.assertEqual(
            res, "<p>Hello <br>world <br> in a multi line <br>paragraph</p>"
        )

    def test_convert_text_and_a_tag(self):
        """test_convert_text_and_a_tag."""
        res = slate_to_html(
            [
                {
                    "children": [
                        {"text": "Hello "},
                        {"children": [{"text": "world"}], "type": "strong"},
                        {"text": " mixed "},
                        {"children": [{"text": "content"}], "type": "i"},
                        {"text": "."},
                    ],
                    "type": "p",
                }
            ]
        )

        self.assertEqual(
            res,
            "<p>Hello <strong>world</strong> mixed <i>content</i>.</p>",
        )

    # def test_convert_case_simple_p(self):
    #    """test_convert_case_simple_p."""
    #    slate = read_json("1.json")
    #    html = slate_to_html(slate)
    #    self.assertEqual(
    #        html,
    #        "<p>Since version 2.0, lxml comes with a dedicated Python package "
    #        "for dealing with HTML: lxml.html. <br>It is based on lxml's HTML "
    #        " parser, but provides a special Element API for HTML elements, as"
    #        " well as a number of utilities for common HTML processing tasks."
    #        "</p>",
    #    )

    def test_convert_case_multiple_p(self):
        """test_convert_case_multiple_p."""
        slate = read_json("2.json")
        html = slate_to_html(slate)
        self.assertEqual(
            html,
            "<p>Since version 2.0, lxml comes with a dedicated Python package "
            "for dealing with HTML: lxml.html. <br>It is based on lxml's HTML "
            "parser, but provides a special Element API for HTML elements, as "
            "well as a number of utilities for common HTML processing tasks."
            "</p><p>The normal HTML parser is capable of handling broken HTML,"
            " but for pages that are far enough from HTML to call them "
            "'tag soup', it may still fail to parse the page in a useful way. "
            "A way to deal with this is ElementSoup, which deploys the "
            "well-known BeautifulSoup parser to build an lxml HTML tree.</p>"
            "<p>However, note that the most common problem with web pages is "
            "the lack of (or the existence of incorrect) encoding declarations."
            " It is therefore often sufficient to only use the encoding "
            "detection of BeautifulSoup, called UnicodeDammit, and to leave "
            "the rest to lxml's own HTML parser, which is several times faster."
            "</p>",
        )

    # def test_one_list_item(self):
    #    """test_one_list_item."""
    #    slate = [
    #        {
    #            "children": [
    #                {"text": ""},
    #                {
    #                    "children": [
    #                        {"text": "Brown bear ("},
    #                        {"children": [{"text": "ursus arctos"}],
    #                         "type": "em"},
    #                        {"text": ") in Italy"},
    #                    ],
    #                    "data": {
    #                        "link": {
    #                            "internal": {
    #                                "internal_link": [
    #                                    {"@id":
    #                                     "/case-study-hub/CS-brown-bears-Italy"
    #                                     }
    #                                ]
    #                            }
    #                        }
    #                    },
    #                    "type": "a",
    #                },
    #                {"text": ""},
    #            ],
    #            "type": "li",
    #        }
    #    ]
    #    text = clean_whitespace(
    #        """<li><a href="/case-study-hub/CS-brown-bears-Italy"
    #    >Brown bear (<em>ursus arctos</em>) in Italy</a>
    #    </li>"""
    #    )
    #    res = slate_to_html(slate)

    #    self.assertEqual(
    #        res,
    #        text,
    #    )

    def test_convert_slate_output_markup(self):
        """test_convert_slate_output_markup."""
        slate = read_json("5.json")
        res = slate_to_html(slate).strip()

        html = read_data("5.html").strip()
        self.assertEqual(res, html)

    def test_slate_list(self):
        """test_slate_list."""
        slate = read_json("6.json")
        res = slate_to_html(slate).strip()
        html = read_data("6-1.html").strip()
        self.assertEqual(res, html)

    # def test_slate_data(self):
    #    """test_slate_data."""
    #    slate = read_json("7.json")
    #    html = slate_to_html(slate).strip()

    #    self.assertTrue("<span data-slate-data=" in html)

    #    self.assertEqual(text_to_slate(html), slate)

    # def test_wrapped_slate_data(self):
    #    """test_wrapped_slate_data."""
    #    slate = read_json("8.json")
    #    html = slate_to_html(slate).strip()

    #    self.assertTrue("<span data-slate-data=" in html)

    #    self.assertEqual(text_to_slate(html), slate)
