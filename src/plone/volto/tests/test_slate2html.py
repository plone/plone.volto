""" Slate2HTML module """

# -*- coding: utf-8 -*-

from pkg_resources import resource_filename
from plone.volto.slate.html2slate import text_to_slate
from plone.volto.slate.slate2html import slate_to_html

import json
import lxml.html
import os
import unittest


def format_html(text):
    e = lxml.html.fromstring(text)
    return lxml.html.tostring(e, pretty_print=True).decode()


def read_data(filename):
    """read_data.

    :param filename:
    """
    fpath = resource_filename("plone.volto", os.path.join("tests/data", filename))

    with open(fpath) as f:
        return f.read()


def read_json(filename):
    """read_json.

    :param filename:
    """
    fpath = resource_filename("plone.volto", os.path.join("tests/data", filename))

    with open(fpath) as f:
        return json.load(f)


class TestConvertSlate2HTML(unittest.TestCase):
    """TestConvertSlate2HTML."""

    maxDiff = None

    def test_convert_simple_string(self):
        """test_convert_simple_string."""
        res = slate_to_html([{"children": [{"text": "Hello world"}], "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")

    def test_convert_simple_paragraph(self):
        """test_convert_simple_paragraph."""
        res = slate_to_html([{"children": [{"text": "Hello world"}], "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")

    def test_convert_simple_paragraph_multi_breaks(self):
        """test_convert_simple_paragraph_multi_breaks."""
        res = slate_to_html(
            [
                {
                    "children": [
                        {"text": "Hello \nworld \n in a multi line \nparagraph"}
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

    def test_convert_case_simple_p(self):
        """test_convert_case_simple_p."""
        slate = read_json("1.json")
        html = slate_to_html(slate)
        self.assertEqual(html, "<p>Since.<br>It is .</p>")

    def test_convert_case_multiple_p(self):
        """test_convert_case_multiple_p."""
        slate = read_json("2.json")
        html = slate_to_html(slate)
        self.assertEqual(
            html,
            "<p>Since version 2.0.<br>It is based."
            "</p><p>The normal HTML parser.</p>"
            "<p>However, note that.</p>",
        )

    def test_one_list_item(self):
        """test_one_list_item."""
        slate = [
            {
                "children": [
                    {"text": ""},
                    {
                        "children": [
                            {"text": "Brown bear ("},
                            {"children": [{"text": "ursus arctos"}], "type": "em"},
                            {"text": ") in Italy"},
                        ],
                        "data": {"url": "/case-study-hub/CS-brown-bears-Italy"},
                        "type": "link",
                    },
                    {"text": ""},
                ],
                "type": "li",
            }
        ]
        text = """<li><a href="/case-study-hub/CS-brown-bears-Italy">Brown bear (<em>ursus arctos</em>) in Italy</a></li>"""
        res = slate_to_html(slate)

        self.assertEqual(
            res,
            text,
        )

    def test_convert_slate_output_markup(self):
        """test_convert_slate_output_markup."""
        slate = read_json("5.json")

        res = slate_to_html(slate).strip()
        html = read_data("5.html").strip()

        self.assertEqual(res, html)

    def test_slate_list(self):
        """test_slate_list."""
        slate = read_json("6.json")
        s = slate_to_html(slate).strip()
        res = format_html(s)
        html = format_html(read_data("6-1.html").strip())
        self.assertEqual(res, html)

    def test_slate_data(self):
        """test_slate_data."""
        slate = read_json("7.json")
        html = slate_to_html(slate).strip()

        self.assertTrue("<span data-slate-data=" in html)

        self.assertEqual(text_to_slate(html), slate)

    def test_wrapped_slate_data(self):
        """test_wrapped_slate_data."""
        slate = read_json("8.json")
        html = slate_to_html(slate).strip()

        self.assertTrue("<span data-slate-data=" in html)

        self.assertEqual(text_to_slate(html), slate)
