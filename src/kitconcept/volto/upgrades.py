from copy import deepcopy
from plone import api
from plone.restapi.behaviors import IBlocks


def from12to13_migrate_listings(context):
    def migrate_listing(originBlocks):
        blocks = deepcopy(originBlocks)
        for blockid in blocks:
            block = blocks[blockid]
            if block["@type"] == "listing":
                if block.get("template", False) and not block.get("variation", False):
                    block["variation"] = block["template"]
                    del block["template"]
                if block.get("template", False) and block.get("variation", False):
                    del block["template"]
                print(f"Migrated listing in {obj.absolute_url()}")

        return blocks

    for brain in api.content.find(object_provides=IBlocks.__identifier__):
        obj = brain.getObject()
        obj.blocks = migrate_listing(obj.blocks)
