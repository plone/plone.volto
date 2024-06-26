from plone import api
from plone.app.linkintegrity.interfaces import IRetriever

import pytest


@pytest.fixture
def retrieve_links():
    def func(content):
        retriever = IRetriever(content)
        return retriever.retrieveLinks()

    return func


@pytest.fixture
def contents(portal) -> dict:
    with api.env.adopt_roles(
        [
            "Manager",
        ]
    ):
        doc1 = api.content.create(
            container=portal,
            type="Document",
            id="doc1",
            title="Document with Blocks",
            description="Description",
        )
        doc2 = api.content.create(
            container=portal,
            type="Document",
            id="doc2",
            UID="e663af38-9111-4dd2-adf9-0bbd135c8a78",
            title="Target Document",
            description="Description",
        )
    return {
        "doc1": doc1,
        "doc2": doc2,
    }


class TestBlocksLinkintegrity:

    @pytest.fixture(autouse=True)
    def _setup(self, http_request, portal, contents):
        self.request = http_request
        self.doc1 = contents["doc1"]
        self.doc2 = contents["doc2"]

    @pytest.mark.parametrize(
        "case,blocks",
        [
            [
                "internal_links_in_nested_columns",
                {
                    "111": {
                        "@type": "__grid",
                        "columns": [
                            {
                                "@type": "teaser",
                                "href": "../resolveuid/e663af38-9111-4dd2-adf9-0bbd135c8a78",
                            }
                        ],
                    },
                },
            ],
            [
                "internal_links_in_nested_hrefList",
                {
                    "111": {
                        "hrefList": [
                            {
                                "href": "../resolveuid/e663af38-9111-4dd2-adf9-0bbd135c8a78",
                            }
                        ],
                    },
                },
            ],
            [
                "internal_links_in_nested_slides",
                {
                    "111": {
                        "@type": "__grid",
                        "columns": [
                            {
                                "@type": "teaser",
                                "href": "../resolveuid/e663af38-9111-4dd2-adf9-0bbd135c8a78",
                            }
                        ],
                    },
                },
            ],
        ],
    )
    def test_links_retriever(self, retrieve_links, case, blocks):
        self.doc1.blocks = blocks
        value = retrieve_links(self.doc1)

        assert len(value) == 1
        assert "../resolveuid/e663af38-9111-4dd2-adf9-0bbd135c8a78" in value
