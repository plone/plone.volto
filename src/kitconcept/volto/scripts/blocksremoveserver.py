"""
time bin/instance -O Plone run scripts/blocksremoveserver.py
    This script search and replace old server name (pre-production)
    for a new one. It searches in all good known places
"""

from plone import api
from plone.restapi.behaviors import IBlocks
from copy import deepcopy

import jq
import sys


def string_href_replace_server(blocks, old, new):
    return (
        jq.compile(f'(.. | .href? | strings) |= sub("{old}";"{new}")')
        .input(blocks)
        .first()
    )


def array_href_replace_server(blocks, old, new):
    return (
        jq.compile(f'(.. | .href? | arrays | .[]."@id") |= sub("{old}";"{new}")')
        .input(blocks)
        .first()
    )


def string_url_replace_server(blocks, old, new):
    return (
        jq.compile(f'(.. | .url? | strings) |= sub("{old}";"{new}")')
        .input(blocks)
        .first()
    )


def array_url_replace_server(blocks, old, new):
    return (
        jq.compile(f'(.. | .url? | arrays | .[]."@id") |= sub("{old}";"{new}")')
        .input(blocks)
        .first()
    )


def array_preview_image_replace_server(blocks, old, new):
    return (
        jq.compile(
            f'(.. | .preview_image? | arrays | .[]."@id") |= sub("{old}";"{new}")'
        )
        .input(blocks)
        .first()
    )


def draftjs_replace_server(blocks, old, new):
    blocks = deepcopy(blocks)
    for blockuid in blocks:
        block = blocks[blockuid]
        if block["@type"] == "text":
            entity_map = block.get("text", {}).get("entityMap", {})
            for entity in entity_map.values():
                if entity.get("type") == "LINK":
                    href = entity.get("data", {}).get("url", "")
                    if href and href.startswith(old):
                        entity["data"]["url"] = entity["data"]["url"].replace(old, new)
    return blocks


if __name__ == "__main__":
    if len(sys.argv) > 3:
        oldservername = sys.argv[3]
    else:
        oldservername = ""

    if len(sys.argv) > 4:
        newservername = sys.argv[4]
    else:
        newservername = ""

    for brain in api.content.find(object_provides=IBlocks.__identifier__):
        obj = brain.getObject()
        blocks = obj.blocks

        # Search for any href field that is an string (old teasers, non object_browser
        # based) and replaces them
        blocks = string_href_replace_server(blocks)

        # Search for any href field that is an array (object_browser) and replaces the @id field
        blocks = array_href_replace_server(blocks)

        # Search for any url field that is an string (old image teasers, non object_browser
        # based) and replaces them
        blocks = string_url_replace_server(blocks)

        # Search for any url field that is an array (object_browser) and replaces the @id field
        blocks = array_url_replace_server(blocks)

        # Search for any preview_image field that is an array (object_browser) and replaces the @id field
        blocks = array_preview_image_replace_server(blocks)

        # Search for any text block and replaces the DraftJS links (old style)
        blocks = draftjs_replace_server(blocks, oldservername, newservername)
