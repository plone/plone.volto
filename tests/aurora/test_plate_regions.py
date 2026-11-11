from plone import api
from plone.volto import aurora

import pytest


PLATE_VALUE = [{"type": "p", "children": [{"text": "Hello aurora"}]}]


def legacy_blocks():
    return {
        "__somersault__": {"@type": "__somersault__", "value": PLATE_VALUE},
        "a1b2": {"@type": "title"},
    }


def migrated_blocks():
    return {
        "main": {"@type": "plate", "value": PLATE_VALUE},
        "a1b2": {"@type": "title"},
    }


class TestMigrateBlocks:
    def test_renames_key_and_type(self):
        assert aurora.migrate_blocks(legacy_blocks()) == migrated_blocks()

    def test_does_not_change_input(self):
        blocks = legacy_blocks()
        aurora.migrate_blocks(blocks)
        assert blocks == legacy_blocks()

    @pytest.mark.parametrize(
        "blocks",
        [
            None,
            {},
            {"a1b2": {"@type": "slate"}},
            {"main": {"@type": "plate", "value": []}},
        ],
    )
    def test_nothing_to_migrate(self, blocks):
        assert aurora.migrate_blocks(blocks) is None

    def test_existing_main_wins(self):
        blocks = {
            "__somersault__": {"@type": "__somersault__", "value": ["old"]},
            "main": {"@type": "plate", "value": ["new"]},
        }
        assert aurora.migrate_blocks(blocks) == {
            "main": {"@type": "plate", "value": ["new"]}
        }

    def test_fixes_legacy_type_in_other_regions(self):
        blocks = {"aboveContent": {"@type": "__somersault__", "value": []}}
        assert aurora.migrate_blocks(blocks) == {
            "aboveContent": {"@type": "plate", "value": []}
        }

    def test_blocks_layout(self):
        layout = {"items": ["a1b2", "__somersault__"]}
        assert aurora.migrate_blocks_layout(layout) == {"items": ["a1b2", "main"]}
        assert aurora.migrate_blocks_layout({"items": ["a1b2"]}) is None


class TestMigrateContent:
    @pytest.fixture(autouse=True)
    def _setup(self, portal):
        self.portal = portal
        with api.env.adopt_roles(["Manager"]):
            self.doc = api.content.create(
                container=portal,
                type="Document",
                id="aurora-doc",
                title="Aurora doc",
                blocks=legacy_blocks(),
                blocks_layout={"items": ["a1b2"]},
            )
        self.modified = self.doc.modified()

    def test_migrate_plate_regions(self):
        paths = aurora.migrate_plate_regions(self.portal)
        assert "/".join(self.doc.getPhysicalPath()) in paths
        assert self.doc.blocks == migrated_blocks()
        assert self.doc.blocks_layout == {"items": ["a1b2"]}
        assert self.doc.modified() == self.modified

    def test_reindexes_block_types(self):
        catalog = api.portal.get_tool("portal_catalog")
        if "block_types" not in catalog.indexes():
            pytest.skip("block_types index not available")
        aurora.migrate_plate_regions(self.portal)
        assert catalog.unrestrictedSearchResults(
            UID=self.doc.UID(), block_types="plate"
        )

    def test_dry_run(self):
        paths = aurora.migrate_plate_regions(self.portal, dry_run=True)
        assert "/".join(self.doc.getPhysicalPath()) in paths
        assert self.doc.blocks == legacy_blocks()

    def test_idempotent(self):
        aurora.migrate_plate_regions(self.portal)
        assert aurora.migrate_plate_regions(self.portal) == []

    def test_site_root(self):
        self.portal.blocks = legacy_blocks()
        paths = aurora.migrate_plate_regions(self.portal)
        assert "/".join(self.portal.getPhysicalPath()) in paths
        assert self.portal.blocks == migrated_blocks()

    def test_install_aurora_profile_migrates(self):
        setup_tool = api.portal.get_tool("portal_setup")
        setup_tool.runAllImportStepsFromProfile("profile-plone.volto:aurora")
        assert self.doc.blocks == migrated_blocks()
        assert setup_tool.getLastVersionForProfile("plone.volto:aurora") == ("1000",)

    def test_other_profiles_do_not_migrate(self):
        setup_tool = api.portal.get_tool("portal_setup")
        setup_tool.runAllImportStepsFromProfile("profile-plone.volto:default")
        assert self.doc.blocks == legacy_blocks()

    def test_run_from_console(self, app, monkeypatch):
        calls = []
        monkeypatch.setattr(aurora, "newSecurityManager", lambda *args: None)
        monkeypatch.setattr(aurora.transaction, "commit", lambda: calls.append(1))
        site_id = self.portal.getId()
        assert aurora.run_from_console(app, ["-O", site_id, "--site", site_id]) == 1
        assert self.doc.blocks == migrated_blocks()
        assert calls == [1]

    def test_run_from_console_dry_run(self, app, monkeypatch):
        monkeypatch.setattr(aurora, "newSecurityManager", lambda *args: None)
        monkeypatch.setattr(aurora.transaction, "abort", lambda: None)
        site_id = self.portal.getId()
        assert aurora.run_from_console(app, ["--site", site_id, "--dry-run"]) == 1
        assert self.doc.blocks == legacy_blocks()

    def test_script_file(self, app, monkeypatch):
        """The script runs like ``bin/instance run`` runs it."""
        from pathlib import Path

        import plone.volto
        import runpy
        import sys

        monkeypatch.setattr(aurora, "newSecurityManager", lambda *args: None)
        monkeypatch.setattr(aurora.transaction, "commit", lambda: None)
        script = (
            Path(plone.volto.__file__).parent / "scripts" / "migrate_plate_regions.py"
        )
        site_id = self.portal.getId()
        monkeypatch.setattr(sys, "argv", [str(script), "--site", site_id])
        runpy.run_path(str(script), init_globals={"app": app}, run_name="__main__")
        assert self.doc.blocks == migrated_blocks()
