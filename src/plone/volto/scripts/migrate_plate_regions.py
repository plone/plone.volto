"""Migrate Aurora content from ``blocks.__somersault__`` to ``blocks.main``.

Moves ``blocks["__somersault__"]`` to ``blocks["main"]`` and sets its
``@type`` to ``plate`` on every object with blocks, in place, without touching
the modification date (https://github.com/plone/aurora/issues/379).

Use it on sites that don't install the ``plone.volto:aurora`` profile, or to run
the migration again. Run it with the Zope instance script, for example::

    bin/instance run path/to/migrate_plate_regions.py --site Plone --dry-run
    bin/instance run path/to/migrate_plate_regions.py --site Plone

or with ``zconsole``::

    zconsole run instance/etc/zope.conf path/to/migrate_plate_regions.py --site Plone

Options:

``--site``
    Id of the Plone site. If left out, every Plone site in the database is
    migrated.
``--dry-run``
    Only list the objects that would be migrated, and commit nothing.
"""

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SpecialUsers import system as system_user
from plone.base.interfaces import IPloneSiteRoot
from plone.volto.aurora import migrate_plate_regions
from Testing.makerequest import makerequest
from zope.component.hooks import setSite

import argparse
import sys
import transaction


def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog="migrate_plate_regions",
        description="Rename blocks.__somersault__ to blocks.main (@type plate).",
    )
    parser.add_argument("--site", help="Id of the Plone site (default: all sites)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the objects that would change, and commit nothing.",
    )
    # The instance script may pass its own options (like ``-O Plone``) on.
    args, _ = parser.parse_known_args(argv)
    return args


def get_sites(app, site_id=None):
    if site_id:
        return [app.unrestrictedTraverse(site_id)]
    return [obj for obj in app.objectValues() if IPloneSiteRoot.providedBy(obj)]


def main(app, argv):
    args = parse_args(argv)
    app = makerequest(app)
    newSecurityManager(None, system_user)
    total = 0
    for site in get_sites(app, args.site):
        setSite(site)
        site_path = "/".join(site.getPhysicalPath())
        paths = migrate_plate_regions(site, dry_run=args.dry_run)
        for path in paths:
            print(path)
        verb = "Would migrate" if args.dry_run else "Migrated"
        print(f"{verb} {len(paths)} objects in {site_path}.")
        total += len(paths)
    if args.dry_run:
        transaction.abort()
        print(f"Dry run: {total} objects would be migrated. Nothing committed.")
    else:
        transaction.get().note("plone.volto: migrate __somersault__ to main")
        transaction.commit()
        print(f"Committed. {total} objects migrated.")
    return total


if __name__ == "__main__":
    # ``app`` is set by ``bin/instance run`` and ``zconsole run``.
    main(app, sys.argv[1:])  # noqa: F821
