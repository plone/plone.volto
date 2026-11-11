"""Plone Aurora support.

In-place migration of the Aurora unified editor content shape
(https://github.com/plone/aurora/issues/379).

The unified editor stored the whole page as one Plate value under
``blocks["__somersault__"]`` with ``"@type": "__somersault__"``. The new shape
names the region by its key and the format by its ``@type``::

    {"blocks": {"main": {"@type": "plate", "value": [...]}}}

The migration can run:

* on install of the ``plone.volto:aurora`` profile, and from the
  ``portal_setup`` Import tab (import step ``plone.volto.aurora-plate-regions``);
* from Python, by calling :func:`migrate_plate_regions`;
* from the command line, with the ``scripts/migrate_plate_regions.py`` script
  run by ``bin/instance run`` or ``zconsole run``.
"""

from copy import deepcopy
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.volto import logger

import transaction


LEGACY_KEY = "__somersault__"
LEGACY_TYPE = "__somersault__"
MAIN_REGION = "main"
PLATE_TYPE = "plate"

# Indexes that depend on the block key or ``@type``.
REINDEX_IDXS = ("SearchableText", "block_types")

MARKER_FILE = "plone.volto.aurora-plate-regions.txt"


def migrate_blocks(blocks: dict) -> dict | None:
    """Return a migrated copy of ``blocks``, or ``None`` if nothing changes.

    * ``blocks["__somersault__"]`` moves to ``blocks["main"]``.
      If ``main`` is already there, it is newer and wins, and the legacy value
      is dropped.
    * Every top-level block with ``"@type": "__somersault__"`` gets
      ``"@type": "plate"``.
    """
    if not isinstance(blocks, dict):
        return None
    changed = False
    new_blocks = deepcopy(blocks)

    if LEGACY_KEY in new_blocks:
        legacy = new_blocks.pop(LEGACY_KEY)
        if MAIN_REGION not in new_blocks:
            new_blocks[MAIN_REGION] = legacy
        changed = True

    for value in new_blocks.values():
        if isinstance(value, dict) and value.get("@type") == LEGACY_TYPE:
            value["@type"] = PLATE_TYPE
            changed = True

    return new_blocks if changed else None


def migrate_blocks_layout(blocks_layout: dict) -> dict | None:
    """Rename ``__somersault__`` in ``blocks_layout["items"]``, if it is there.

    Regions are not meant to be in the layout, but keep the layout consistent
    with ``blocks`` if an older version put it there.
    """
    if not isinstance(blocks_layout, dict):
        return None
    items = blocks_layout.get("items")
    if not isinstance(items, list) or LEGACY_KEY not in items:
        return None
    new_items = []
    for item in items:
        if item == LEGACY_KEY:
            item = MAIN_REGION
        if item not in new_items:
            new_items.append(item)
    return {**blocks_layout, "items": new_items}


def migrate_object(obj, dry_run: bool = False, reindex: bool = True) -> bool:
    """Migrate one object in place. Return ``True`` if it needs (or got) changes.

    ``modified`` is left untouched: the content did not change for editors.
    """
    blocks = getattr(obj.aq_base, "blocks", None)
    new_blocks = migrate_blocks(blocks)
    if new_blocks is None:
        return False
    if dry_run:
        return True
    obj.blocks = new_blocks
    new_layout = migrate_blocks_layout(getattr(obj.aq_base, "blocks_layout", None))
    if new_layout is not None:
        obj.blocks_layout = new_layout
    if reindex:
        catalog = api.portal.get_tool("portal_catalog")
        idxs = [idx for idx in REINDEX_IDXS if idx in catalog.indexes()]
        # Passing explicit idxs does not call notifyModified, so the
        # modification date stays as it is.
        obj.reindexObject(idxs=idxs)
    return True


def _iter_blocks_objects(portal):
    """Yield the site root and every catalogued object that provides IBlocks."""
    yield portal
    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog.unrestrictedSearchResults(object_provides=IBlocks.__identifier__)
    for brain in brains:
        try:
            obj = brain._unrestrictedGetObject()
        except (AttributeError, KeyError):
            logger.warning(f"Could not get object at {brain.getPath()}, skipping.")
            continue
        yield obj


def migrate_plate_regions(
    portal=None, dry_run: bool = False, savepoint_every: int = 250
) -> list[str]:
    """Migrate every object with blocks in the site.

    Returns the paths of the objects that were migrated, or that would be
    migrated when ``dry_run`` is ``True``. It does not commit the transaction.
    """
    if portal is None:
        portal = api.portal.get()
    prefix = "[dry-run] " if dry_run else ""
    migrated = []
    for obj in _iter_blocks_objects(portal):
        if migrate_object(obj, dry_run=dry_run):
            path = "/".join(obj.getPhysicalPath())
            migrated.append(path)
            logger.info(f"{prefix}Migrated plate regions in {path}")
            if not dry_run and len(migrated) % savepoint_every == 0:
                transaction.savepoint(optimistic=True)
    logger.info(
        f"{prefix}Migrated {LEGACY_KEY!r} to {MAIN_REGION!r} "
        f"in {len(migrated)} objects."
    )
    return migrated


def import_plate_regions(context):
    """GenericSetup import step: run the migration for the aurora profile.

    It only runs for profiles that ship the marker file, so it does nothing
    when other profiles are imported.
    """
    if context.readDataFile(MARKER_FILE) is None:
        return
    migrate_plate_regions(context.getSite())
