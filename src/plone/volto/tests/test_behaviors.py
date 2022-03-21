from plone.volto.behaviors import preview
from plone.volto.testing import PLONE_VOLTO_CORE_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility
from zope.component import queryUtility

import unittest


class PreviewBehaviorTest(unittest.TestCase):

    layer = PLONE_VOLTO_CORE_INTEGRATION_TESTING

    BEHAVIOR = "volto.preview"

    CONTENT_TYPES_WITH_PREVIEW_FIELDS = ["Document", "Event"]

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    @staticmethod
    def get_behaviors(portal_type: str) -> list:
        """Return a list of content type behaviors."""
        fti = queryUtility(IDexterityFTI, name=portal_type)
        return list(fti.behaviors)

    def test_behavior_volto_preview(self):
        behavior = getUtility(IBehavior, self.BEHAVIOR)
        self.assertEqual(
            behavior.marker,
            preview.IPreview,
        )

    def test_applied_in_contenttypes(self):
        for contenttype in self.CONTENT_TYPES_WITH_PREVIEW_FIELDS:
            self.assertIn(self.BEHAVIOR, self.get_behaviors(contenttype))
