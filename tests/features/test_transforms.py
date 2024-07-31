from plone import api

import pytest


class TestBlocksTransforms:

    @pytest.fixture(autouse=True)
    def _setup(self, app, http_request, portal, contents):
        self.app = app
        self.portal = portal
        self.request = http_request
        self.doc = contents["doc"]
        self.image = contents["image"]

    def test_deserialize_nested_fields_resolveuid(self, deserialize):
        doc = self.doc
        deserialize(
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [
                        {
                            "href": doc.absolute_url(),
                            "preview_image": self.image.absolute_url(),
                        }
                    ],
                }
            },
            context=doc,
        )
        doc_uid = api.content.get_uuid(doc)
        image_uid = api.content.get_uuid(self.image)

        assert doc.blocks["123"]["columns"][0]["href"] == f"../resolveuid/{doc_uid}"
        assert (
            doc.blocks["123"]["columns"][0]["preview_image"]
            == f"../resolveuid/{image_uid}"
        )

    def test_deserialize_nested_fields_arrayed_resolveuid(self, deserialize):
        doc = self.doc
        deserialize(
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": [doc.absolute_url()]}],
                }
            },
            context=doc,
        )
        doc_uid = api.content.get_uuid(doc)
        assert doc.blocks["123"]["columns"][0]["href"][0] == f"../resolveuid/{doc_uid}"

    def test_deserialize_nested_fields_arrayed_object_browser_resolveuid(
        self, deserialize
    ):
        doc = self.doc
        deserialize(
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": [{"@id": doc.absolute_url()}]}],
                }
            },
            context=doc,
        )
        doc_uid = api.content.get_uuid(doc)

        assert (
            doc.blocks["123"]["columns"][0]["href"][0]["@id"]
            == f"../resolveuid/{doc_uid}"
        )

    def test_serialize_nested_fields_resolveuid(self, serialize):
        doc = self.doc
        doc_uid = api.content.get_uuid(doc)
        image_uid = api.content.get_uuid(self.image)
        value = serialize(
            context=doc,
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [
                        {
                            "href": f"../resolveuid/{doc_uid}",
                            "preview_image": f"../resolveuid/{image_uid}",
                        }
                    ],
                }
            },
        )

        assert value["123"]["columns"][0]["href"] == doc.absolute_url()
        assert value["123"]["columns"][0]["preview_image"] == self.image.absolute_url()

    def test_serialize_nested_fields_arrayed_resolveuid(self, serialize):
        doc = self.doc
        doc_uid = api.content.get_uuid(doc)
        value = serialize(
            context=doc,
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": [f"../resolveuid/{doc_uid}"]}],
                }
            },
        )

        assert value["123"]["columns"][0]["href"][0] == doc.absolute_url()

    def test_serialize_nested_fields_arrayed_object_browser_resolveuid(self, serialize):
        doc = self.doc
        doc_uid = api.content.get_uuid(doc)
        value = serialize(
            context=doc,
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": [{"@id": f"../resolveuid/{doc_uid}"}]}],
                }
            },
        )

        assert value["123"]["columns"][0]["href"][0]["@id"] == doc.absolute_url()

    def test_deserialize_slate(self, deserialize):
        portal_url = self.portal.absolute_url()
        doc = self.doc
        res = deserialize(
            blocks={
                "e248ecb5-b787-4e04-b1b3-98febf4539d1": {
                    "@type": "__grid",
                    "columns": [
                        {
                            "@type": "slate",
                            "id": "5abdabe7-e8b8-4a9b-8b92-9ab1dcd83b71",
                            "value": [
                                {
                                    "type": "p",
                                    "children": [
                                        {"text": "this is a "},
                                        {
                                            "children": [
                                                {"text": ""},
                                                {
                                                    "type": "a",
                                                    "children": [
                                                        {"text": "slate link"}
                                                    ],
                                                    "data": {
                                                        "link": {
                                                            "internal": {
                                                                "internal_link": [
                                                                    {
                                                                        "@id": f"{portal_url}/image1",
                                                                        "title": "Image 1",
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    },
                                                },
                                                {"text": ""},
                                            ],
                                            "type": "strong",
                                        },
                                        {"text": " inside some text"},
                                    ],
                                }
                            ],
                            "plaintext": "this is a slate link inside some text",
                        }
                    ],
                }
            },
            context=doc,
        )

        value = res.blocks["e248ecb5-b787-4e04-b1b3-98febf4539d1"]["columns"][0][
            "value"
        ]
        link = value[0]["children"][1]["children"][1]
        resolve_link = link["data"]["link"]["internal"]["internal_link"][0]["@id"]
        assert resolve_link.startswith("../resolveuid/") is True

    def test_serialize_slate(self, serialize):
        doc = self.doc
        doc_uid = api.content.get_uuid(doc)
        resolve_uid_link = {
            "@id": f"../resolveuid/{doc_uid}",
            "title": "Welcome to Plone",
        }
        blocks = {
            "e248ecb5-b787-4e04-b1b3-98febf4539d1": {
                "@type": "__grid",
                "columns": [
                    {
                        "@type": "slate",
                        "plaintext": "this is a slate link inside some text",
                        "value": [
                            {
                                "children": [
                                    {"text": "this is a "},
                                    {
                                        "children": [
                                            {"text": ""},
                                            {
                                                "children": [{"text": "slate link"}],
                                                "data": {
                                                    "link": {
                                                        "internal": {
                                                            "internal_link": [
                                                                resolve_uid_link
                                                            ]
                                                        }
                                                    }
                                                },
                                                "type": "a",
                                            },
                                            {"text": ""},
                                        ],
                                        "type": "strong",
                                    },
                                    {"text": " inside some text"},
                                ],
                                "type": "p",
                            }
                        ],
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }

        res = serialize(context=doc, blocks=blocks)

        value = res["e248ecb5-b787-4e04-b1b3-98febf4539d1"]["columns"][0]["value"]
        link = value[0]["children"][1]["children"][1]
        resolve_link = link["data"]["link"]["internal"]["internal_link"][0]["@id"]

        assert resolve_link == f"{self.portal.absolute_url()}/doc1"
