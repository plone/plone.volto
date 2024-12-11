from plone import api
from plone.dexterity.utils import iterSchemata
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IFieldSerializer
from plone.volto.testing import PLONE_VOLTO_CORE_ACCEPTANCE_TESTING
from plone.volto.testing import PLONE_VOLTO_CORE_FUNCTIONAL_TESTING
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING
from plone.volto.testing import PLONE_VOLTO_CORESANDBOX_ACCEPTANCE_TESTING
from plone.volto.testing import PLONE_VOLTO_CORESANDBOX_FUNCTIONAL_TESTING
from plone.volto.testing import PLONE_VOLTO_CORESANDBOX_INTEGRATION_TESTING
from plone.volto.testing import PLONE_VOLTO_MIGRATION_FUNCTIONAL_TESTING
from plone.volto.testing import PLONE_VOLTO_MIGRATION_INTEGRATION_TESTING
from pytest_plone import fixtures_factory
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter

import json
import pytest


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory(
        (
            (PLONE_VOLTO_CORE_ACCEPTANCE_TESTING, "acceptance"),
            (PLONE_VOLTO_CORE_FUNCTIONAL_TESTING, "functional"),
            (PLONE_VOLTO_CORE_INTEGRATION_TESTING, "integration"),
            (PLONE_VOLTO_CORESANDBOX_ACCEPTANCE_TESTING, "coresandbox_acceptance"),
            (PLONE_VOLTO_CORESANDBOX_FUNCTIONAL_TESTING, "coresandbox_functional"),
            (PLONE_VOLTO_CORESANDBOX_INTEGRATION_TESTING, "coresandbox_integration"),
            (PLONE_VOLTO_MIGRATION_FUNCTIONAL_TESTING, "migration_functional"),
            (PLONE_VOLTO_MIGRATION_INTEGRATION_TESTING, "migration_integration"),
        )
    )
)


@pytest.fixture
def distribution_name() -> str:
    """Distribution name."""
    return "volto"


@pytest.fixture
def contents(portal) -> dict:
    with api.env.adopt_roles(
        [
            "Manager",
        ]
    ):
        doc = api.content.create(
            container=portal,
            type="Document",
            id="doc1",
            title="Lorem Ipsum",
            description="Description",
        )
        image = api.content.create(
            container=portal,
            type="Image",
            id="image1",
            title="Target image",
        )
    return {
        "doc": doc,
        "image": image,
    }


@pytest.fixture
def serialize(http_request):
    def func(context, blocks):
        fieldname = "blocks"
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((context, field), IDataManager)
        dm.set(blocks)
        serializer = getMultiAdapter((field, context, http_request), IFieldSerializer)
        return serializer()

    return func


@pytest.fixture
def deserialize(http_request):
    def func(blocks=None, validate_all=False, context=None):
        request = http_request
        blocks = blocks or ""
        context = context
        request["BODY"] = json.dumps({"blocks": blocks})
        deserializer = getMultiAdapter((context, request), IDeserializeFromJson)
        return deserializer(validate_all=validate_all)

    return func
