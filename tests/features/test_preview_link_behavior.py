from plone import api
from plone.dexterity.schema import invalidate_cache
from plone.namedfile.file import NamedBlobImage
from plone.restapi.interfaces import ISerializeToJsonSummary
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter
from zope.component.hooks import setSite
from zope.lifecycleevent import modified

import pytest


TEST_GIF = (
    b"GIF89a\x01\x00\x01\x00\x00\xff\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
)


@pytest.fixture
def portal(app, get_fti):
    portal = app["plone"]
    setSite(portal)
    fti = get_fti("Document")
    base_behaviors = fti.behaviors
    fti.behaviors += ("volto.preview_image_link",)
    invalidate_cache(fti)
    yield portal
    fti.behaviors = base_behaviors
    invalidate_cache(fti)


@pytest.fixture
def contents(portal) -> dict:
    from plone.volto.behaviors.preview_link import IPreviewLink

    with api.env.adopt_roles(
        [
            "Manager",
        ]
    ):
        doc = api.content.create(
            container=portal, type="Document", id="doc1", title="Document"
        )
        image = api.content.create(
            container=portal,
            type="Image",
            id="image-1",
            title="Target image",
            image=NamedBlobImage(data=TEST_GIF, filename="test.gif"),
        )
        dm = getMultiAdapter((doc, IPreviewLink["preview_image_link"]), IDataManager)
        dm.set(image)
        modified(doc)
    return {"doc": doc, "image": image}


class TestPreviewLinkBehavior:

    @pytest.fixture(autouse=True)
    def _setup(self, portal, contents):
        self.doc = contents["doc"]
        self.image = contents["image"]

    def test_image_scales_includes_preview_image_link(self, http_request):
        brain = api.content.find(UID=self.doc.UID())[0]
        summary = getMultiAdapter((brain, http_request), ISerializeToJsonSummary)()
        assert "preview_image_link" in summary["image_scales"]

        # Make sure scales are updated if image is edited
        self.image.image = None
        modified(self.image)

        brain = api.content.find(UID=self.doc.UID())[0]
        summary2 = getMultiAdapter((brain, http_request), ISerializeToJsonSummary)()
        assert summary["image_scales"] != summary2["image_scales"]
