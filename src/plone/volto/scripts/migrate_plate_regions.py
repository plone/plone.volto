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

The logic lives in :func:`plone.volto.aurora.run_from_console`, next to the
``post_handler`` of the ``plone.volto:aurora`` profile, and both call
:func:`plone.volto.aurora.migrate_plate_regions`.
"""

from plone.volto.aurora import run_from_console

import sys


if __name__ == "__main__":
    # ``app`` is set by ``bin/instance run`` and ``zconsole run``.
    run_from_console(app, sys.argv[1:])  # noqa: F821
