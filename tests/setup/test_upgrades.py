from plone import api
from plone.volto import PACKAGE_NAME
from plone.volto.upgrades import from12to13_migrate_listings

import pytest


class TestUpgrades:

    @pytest.fixture(autouse=True)
    def _setup(self, app, http_request, portal, contents):
        self.app = app
        self.request = http_request
        self.doc = contents["doc"]
        self.image = contents["image"]

    @pytest.mark.parametrize(
        "blocks,expected",
        [
            [
                {"123": {"@type": "listing", "template": "summary"}},
                {"@type": "listing", "variation": "summary", "querystring": {}},
            ],
            [
                {"123": {"@type": "listing", "query": []}},
                {"@type": "listing", "querystring": {"query": []}},
            ],
            [
                {"123": {"@type": "listing", "variation": "summary", "query": []}},
                {
                    "@type": "listing",
                    "variation": "summary",
                    "querystring": {"query": []},
                },
            ],
            [
                {
                    "123": {
                        "@type": "listing",
                        "template": "summary",
                        "variation": "summary",
                        "query": [],
                    }
                },
                {
                    "@type": "listing",
                    "variation": "summary",
                    "querystring": {"query": []},
                },
            ],
            [
                {
                    "123": {
                        "@type": "listing",
                        "template": "summary",
                        "variation": "summary",
                        "query": [],
                    },
                    "222": {"@type": "image", "url": ""},
                },
                {
                    "@type": "listing",
                    "variation": "summary",
                    "querystring": {"query": []},
                },
            ],
        ],
    )
    def test_upgradefrom12to13listing_block(self, deserialize, blocks, expected):
        doc = self.doc
        deserialize(blocks=blocks, context=doc)
        from12to13_migrate_listings(self.app)
        assert self.doc.blocks["123"] == expected

    @pytest.mark.parametrize(
        "blocks,expected",
        [
            [
                {
                    "123": {
                        "@type": "listing",
                        "id": "87def7d6-e019-4026-a8a2-e1c289941fac",
                        "limit": "2",
                        "sort_on": "created",
                        "sort_order": True,
                        "batch_size": "10",
                        "depth": "3",
                        "query": [
                            {
                                "i": "path",
                                "o": "plone.app.querystring.operation.string.absolutePath",
                                "v": "/de/beispiele",
                            },
                            {
                                "i": "portal_type",
                                "o": "plone.app.querystring.operation.selection.any",
                                "v": ["Document"],
                            },
                        ],
                        "template": "newsListing",
                    }
                },
                {
                    "@type": "listing",
                    "id": "87def7d6-e019-4026-a8a2-e1c289941fac",
                    "querystring": {
                        "limit": "2",
                        "sort_on": "created",
                        "sort_order": "descending",
                        "b_size": "10",
                        "depth": "3",
                        "sort_order_boolean": True,
                        "query": [
                            {
                                "i": "path",
                                "o": "plone.app.querystring.operation.string.absolutePath",
                                "v": "/de/beispiele",
                            },
                            {
                                "i": "portal_type",
                                "o": "plone.app.querystring.operation.selection.any",
                                "v": ["Document"],
                            },
                        ],
                    },
                    "variation": "newsListing",
                },
            ],
            [
                {"123": {"@type": "listing", "query": []}},
                {"@type": "listing", "querystring": {"query": []}},
            ],
        ],
    )
    def test_upgradefrom12to13listing_block_query_part(
        self, deserialize, blocks, expected
    ):
        doc = self.doc
        deserialize(blocks=blocks, context=doc)
        from12to13_migrate_listings(self.app)

        assert self.doc.blocks["123"] == expected


class TestUpgrade1101To1102:
    profile_id = f"{PACKAGE_NAME}:default"

    @pytest.fixture(autouse=True)
    def _setup(self, portal):
        self.setup_tool = api.portal.get_tool("portal_setup")
        self.portal_actions = api.portal.get_tool("portal_actions")
        # Simulate a site still at 1101, before personal_tools existed
        self.portal_actions.manage_delObjects(["personal_tools"])
        self.setup_tool.setLastVersionForProfile(self.profile_id, "1101")

    def test_upgrade_adds_personal_tools(self):
        assert "personal_tools" not in self.portal_actions.objectIds()
        self.setup_tool.upgradeProfile(self.profile_id, dest="1102")
        assert "personal_tools" in self.portal_actions.objectIds()
        category = self.portal_actions["personal_tools"]
        assert list(category.objectIds()) == [
            "profile",
            "preferences",
            "plone_setup",
        ]

    def test_upgrade_sets_profile_version(self):
        self.setup_tool.upgradeProfile(self.profile_id, dest="1102")
        version = self.setup_tool.getLastVersionForProfile(self.profile_id)
        assert version == ("1102",)
