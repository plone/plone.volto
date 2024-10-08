"""
bin/instance -O Plone run scripts/migrate-richtext.py
    Migrate all richtexts to slate blocks.
    Requires a instance of https://github.com/plone/blocks-conversion-tool to run
    on http://localhost:5000/html (the default)
    For more control use the form @@migrate_richtext

"""

from plone import api
from plone.volto.browser.migrate_richtext import migrate_richtext_to_slate


if __name__ == "__main__":
    portal_types = api.portal.get_tool("portal_types")
    portal_types = []
    for fti in portal_types.listTypeInfo():
        behaviors = getattr(fti, "behaviors", [])
        if "volto.blocks" in behaviors:
            portal_types.append(fti.id)

    migrate_richtext_to_slate(portal_types=portal_types)
