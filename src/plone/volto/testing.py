# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import plone.volto
import plone.volto.coresandbox


try:
    from Products.CMFPlone.factory import PLONE60MARKER

    PLONE60MARKER  # pyflakes
except ImportError:
    PLONE_6 = False
else:
    PLONE_6 = True


class PloneVoltoCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.volto)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        api.content.create(
            type="Document", id="front-page", title="Welcome", container=portal
        )
        logout()
        applyProfile(portal, "plone.volto:default")


PLONE_VOLTO_CORE_FIXTURE = PloneVoltoCoreLayer()


PLONE_VOLTO_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_VOLTO_CORE_FIXTURE,), name="PloneVoltoCoreLayer:IntegrationTesting"
)


PLONE_VOLTO_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_VOLTO_CORE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoCoreLayer:FunctionalTesting",
)


PLONE_VOLTO_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PLONE_VOLTO_CORE_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoCoreLayer:AcceptanceTesting",
)


class PloneVoltoCoreSandboxLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.volto)
        self.loadZCML(package=plone.volto.coresandbox)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        api.content.create(
            type="Document", id="front-page", title="Welcome", container=portal
        )
        logout()
        applyProfile(portal, "plone.volto:coresandbox")


PLONE_VOLTO_CORESANDBOX_FIXTURE = PloneVoltoCoreSandboxLayer()


PLONE_VOLTO_CORESANDBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_VOLTO_CORESANDBOX_FIXTURE,),
    name="PloneVoltoCoreSandboxLayer:IntegrationTesting",
)


PLONE_VOLTO_CORESANDBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_VOLTO_CORESANDBOX_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoCoreSandboxLayer:FunctionalTesting",
)


PLONE_VOLTO_CORESANDBOX_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PLONE_VOLTO_CORESANDBOX_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="PloneVoltoCoreSandboxLayer:AcceptanceTesting",
)


class PloneVoltoMigrationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=plone.volto)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        api.content.create(
            type="Document", id="front-page", title="Welcome", container=portal
        )
        logout()


PLONE_VOLTO_MIGRATION_FIXTURE = PloneVoltoMigrationLayer()


PLONE_VOLTO_MIGRATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_VOLTO_MIGRATION_FIXTURE,),
    name="PloneVoltoMigrationLayer:IntegrationTesting",
)


PLONE_VOLTO_MIGRATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_VOLTO_MIGRATION_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoMigrationLayer:FunctionalTesting",
)
