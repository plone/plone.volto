from plone import api
from plone.restapi.behaviors import IBlocks
from collections import Counter

import sys


def audit_blocks():
    types = []
    for brain in api.content.find(object_provides=IBlocks.__identifier__):
        obj = brain.getObject()
        blocks = obj.blocks
        for blockuid in blocks:
            block = blocks[blockuid]
            if (
                block["@type"] != "text"
                and block["@type"] != "image"
                and block["@type"] != "html"
                and block["@type"] != "title"
            ):
                types.append(block["@type"])

    count = Counter(types)
    print(count.most_common())


def where_is_this_block():
    for brain in api.content.find(object_provides=IBlocks.__identifier__):
        obj = brain.getObject()
        blocks = obj.blocks
        for blockuid in blocks:
            block = blocks[blockuid]
            if block["@type"] == sys.argv[3]:
                print(f'{block["@type"]} -> {obj.absolute_url()}')


if len(sys.argv) > 3:
    where_is_this_block()
else:
    audit_blocks()
