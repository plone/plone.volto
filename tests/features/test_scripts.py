from plone.volto.scripts.listingaddsummary import migrate_listing_block_to_summary
from plone.volto.scripts.searchscalesinimageblocks import remove_image_scales

import pytest


class TestScripts:

    @pytest.fixture(autouse=True)
    def _setup(self, http_request, portal, contents):
        self.request = http_request
        self.doc = contents["doc"]
        self.image = contents["image"]

    def test_migrate_listing_block_to_summary(self):
        blocks = {"@type": "listing"}
        result = migrate_listing_block_to_summary(blocks)
        assert result["template"] == "summary"

    def test_remove_image_scales(self):
        blocks = {
            "b53feefa-e6f7-42f0-8f04-534655c6c594": {
                "@type": "image",
                "url": "/foo/bar/@@images/image/large",
            }
        }

        result = remove_image_scales(blocks)
        assert result["b53feefa-e6f7-42f0-8f04-534655c6c594"]["url"] == "/foo/bar"
        assert result["b53feefa-e6f7-42f0-8f04-534655c6c594"]["size"] == "l"

    def test_remove_image_scales_no_large(self):
        blocks = {
            "b53feefa-e6f7-42f0-8f04-534655c6c594": {
                "@type": "image",
                "url": "/foo/bar/@@images/image/teaser",
            }
        }
        result = remove_image_scales(blocks)
        assert result["b53feefa-e6f7-42f0-8f04-534655c6c594"]["url"] == "/foo/bar"
