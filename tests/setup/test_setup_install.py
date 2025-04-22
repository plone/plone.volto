from plone.volto import PACKAGE_NAME

import pytest


class TestSetupInstall:
    def test_addon_installed(self, installer):
        """Test if plone.volto is installed."""
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from plone.volto.interfaces import IPloneVoltoCoreLayer

        assert IPloneVoltoCoreLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1019"

    @pytest.mark.parametrize(
        "portal_type,behavior",
        [
            ["Document", "volto.blocks"],
            ["Document", "volto.preview_image_link"],
            ["Event", "volto.blocks"],
            ["Event", "volto.preview_image_link"],
            ["News Item", "volto.blocks"],
            ["Plone Site", "volto.blocks"],
        ],
    )
    def test_portal_type_has_behavior(
        self, portal, get_behaviors, portal_type: str, behavior: str
    ):
        assert behavior in get_behaviors(portal_type)

    @pytest.mark.parametrize(
        "portal_type,expected",
        [
            ["Document", True],
            ["Event", True],
            ["News Item", True],
            ["Plone Site", False],
            ["Collection", False],
            ["Folder", False],
        ],
    )
    def test_portal_type_global_allow(
        self, portal, get_fti, portal_type: str, expected: bool
    ):
        fti = get_fti(portal_type)
        assert fti.global_allow is expected
