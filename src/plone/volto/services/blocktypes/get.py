from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import collections


@implementer(IPublishTraverse)
class BlockTypesGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.block_type = None

    def publishTraverse(self, request, name):
        self.block_type = name
        return self

    def reply(self):
        catalog = api.portal.get_tool(name="portal_catalog")
        request_body = self.request.form
        result = {}
        type = self.block_type

        query = {
            "object_provides": IBlocks.__identifier__,
        }

        if request_body.get("path"):
            query["path"] = request_body["path"]

        if type:
            result.setdefault("items", [])
            query["block_types"] = self.block_type
            brains = catalog.unrestrictedSearchResults(**query)

            for brain in brains:
                result["items"].append(
                    {
                        "@id": brain.getURL(),
                        "title": brain.Title,
                        "count": brain.block_types[self.block_type],
                    }
                )
        else:
            result.setdefault("summary", {})
            brains = catalog.unrestrictedSearchResults(**query)
            block_types_total = collections.Counter()

            for brain in brains:
                block_types_total.update(brain.block_types)

            for block_type, count in block_types_total.items():
                result["summary"][block_type] = count

        return result
