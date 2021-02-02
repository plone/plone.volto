# -*- coding: utf-8 -*-

from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.interfaces import IDeserializeFromJson
from kitconcept.volto.testing import KITCONCEPTVOLTO_CORE_INTEGRATION_TESTING  # noqa
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import queryUtility
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IFieldSerializer
from z3c.form.interfaces import IDataManager

import json
import unittest


class TestBlocksTransforms(unittest.TestCase):

    layer = KITCONCEPTVOLTO_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.portal.invokeFactory(
            "Document",
            id=u"doc1",
        )
        self.image = self.portal[
            self.portal.invokeFactory("Image", id="image-1", title="Target image")
        ]

    def deserialize(self, blocks=None, validate_all=False, context=None):
        blocks = blocks or ""
        context = context or self.portal.doc1
        self.request["BODY"] = json.dumps({"blocks": blocks})
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)

        return deserializer(validate_all=validate_all)

    def serialize(self, context, blocks):
        fieldname = "blocks"
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((context, field), IDataManager)
        dm.set(blocks)
        serializer = getMultiAdapter((field, context, self.request), IFieldSerializer)
        return serializer()

    def test_deserialize_nested_fields_resolveuid(self):
        self.deserialize(
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": self.portal.doc1.absolute_url()}],
                }
            }
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["columns"][0]["href"],
            "../resolveuid/{}".format(doc_uid),
        )

    def test_deserialize_nested_fields_arrayed_resolveuid(self):
        self.deserialize(
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": [self.portal.doc1.absolute_url()]}],
                }
            }
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["columns"][0]["href"][0],
            "../resolveuid/{}".format(doc_uid),
        )

    def test_deserialize_nested_fields_arrayed_object_browser_resolveuid(self):
        self.deserialize(
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": [{"@id": self.portal.doc1.absolute_url()}]}],
                }
            }
        )
        doc_uid = IUUID(self.portal.doc1)

        self.assertEqual(
            self.portal.doc1.blocks["123"]["columns"][0]["href"][0]["@id"],
            "../resolveuid/{}".format(doc_uid),
        )

    def test_serialize_nested_fields_resolveuid(self):
        doc_uid = IUUID(self.portal.doc1)
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": "../resolveuid/{}".format(doc_uid)}],
                }
            },
        )

        self.assertEqual(
            value["123"]["columns"][0]["href"], self.portal.doc1.absolute_url()
        )

    def test_serialize_nested_fields_arrayed_resolveuid(self):
        doc_uid = IUUID(self.portal.doc1)
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [{"href": ["../resolveuid/{}".format(doc_uid)]}],
                }
            },
        )

        self.assertEqual(
            value["123"]["columns"][0]["href"][0], self.portal.doc1.absolute_url()
        )

    def test_serialize_nested_fields_arrayed_object_browser_resolveuid(self):
        doc_uid = IUUID(self.portal.doc1)
        value = self.serialize(
            context=self.portal.doc1,
            blocks={
                "123": {
                    "@type": "teaserGrid",
                    "columns": [
                        {"href": [{"@id": "../resolveuid/{}".format(doc_uid)}]}
                    ],
                }
            },
        )

        self.assertEqual(
            value["123"]["columns"][0]["href"][0]["@id"],
            self.portal.doc1.absolute_url(),
        )
