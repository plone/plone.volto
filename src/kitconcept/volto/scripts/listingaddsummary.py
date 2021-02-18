"""
time bin/instance -O Plone run scripts/blocksremoveserver.py
    This script search and replace old server name (pre-production)
    for a new one. It searches in all good known places
"""

from plone import api
from plone.restapi.behaviors import IBlocks


def migrate_listing_block_to_summary(block):
    if not block.get("template", False):
        block["template"] = "summary"

    return block


if __name__ == "__main__":
    for brain in api.content.find(object_provides=IBlocks.__identifier__):
        obj = brain.getObject()
        blocks = obj.blocks

        for blockuid in blocks:
            block = blocks[blockuid]
            if block["@type"] == "listing":
                migrate_listing_block_to_summary(block)
