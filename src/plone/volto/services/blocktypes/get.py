from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


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
        result = {"items": []}
        type = self.block_type

        query = {
            "object_provides": IBlocks.__identifier__,
            "block_types": self.block_type,
        }

        if request_body.get("path"):
            query["path"] = request_body["path"]

        if type:
            brains = catalog.unrestrictedSearchResults(**query)

            for brain in brains:
                result["items"].append(
                    {
                        "@id": brain.getURL(),
                        "title": brain.Title,
                        "count": brain.block_types[self.block_type],
                    }
                )

        return result
