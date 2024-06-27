from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.distribution.testing.layer import PloneDistributionFixture
from plone.testing import z2

import plone.app.caching  # noQA
import plone.app.discussion  # noQA
import plone.app.iterate  # noQA
import plone.app.multilingual  # noQA
import plone.app.upgrade  # noQA
import plone.volto  # noQA
import plone.volto.coresandbox  # noQA
import Products.CMFPlacefulWorkflow  # noQA


ANSWERS = {
    "site_id": "plone",
    "title": "Plone Site",
    "description": "A Plone Site with Volto",
    "site_logo": "name=teste;data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",  # noQA
    "default_language": "en",
    "portal_timezone": "America/Sao_Paulo",
    "setup_content": True,
}


class BaseFixture(PloneDistributionFixture):
    PACKAGE_NAME = "plone.volto"
    SITES = (("default", ANSWERS),)
    _distribution_products = (
        ("plone.app.contenttypes", {"loadZCML": True}),
        ("plone.app.caching", {"loadZCML": True}),
        ("plone.app.iterate", {"loadZCML": True}),
        ("plone.app.multilingual", {"loadZCML": True}),
        ("plone.app.upgrade", {"loadZCML": True}),
        ("Products.CMFPlacefulWorkflow", {"loadZCML": True}),
        ("plone.restapi", {"loadZCML": True}),
        ("plone.distribution", {"loadZCML": True}),
    )


BASE_FIXTURE = BaseFixture()


class PloneVoltoCoreLayer(PloneSandboxLayer):

    defaultBases = (BASE_FIXTURE,)


CORE_FIXTURE = PloneVoltoCoreLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(CORE_FIXTURE,), name="PloneVoltoCoreLayer:IntegrationTesting"
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CORE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoCoreLayer:FunctionalTesting",
)


ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(CORE_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoCoreLayer:AcceptanceTesting",
)


class SandboxFixture(BaseFixture):
    _distribution_products = (
        ("plone.app.contenttypes", {"loadZCML": True}),
        ("plone.app.caching", {"loadZCML": True}),
        ("plone.app.iterate", {"loadZCML": True}),
        ("plone.app.multilingual", {"loadZCML": True}),
        ("plone.app.upgrade", {"loadZCML": True}),
        ("Products.CMFPlacefulWorkflow", {"loadZCML": True}),
        ("plone.restapi", {"loadZCML": True}),
        ("plone.distribution", {"loadZCML": True}),
        ("plone.volto.coresandbox", {"loadZCML": True}),
    )


SANDBOX_FIXTURE = SandboxFixture()


class PloneVoltoCoreSandboxLayer(PloneSandboxLayer):

    defaultBases = (SANDBOX_FIXTURE,)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.volto:coresandbox")


CORESANDBOX_FIXTURE = PloneVoltoCoreSandboxLayer()


CORESANDBOX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CORESANDBOX_FIXTURE,),
    name="PloneVoltoCoreSandboxLayer:IntegrationTesting",
)


CORESANDBOX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CORESANDBOX_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoCoreSandboxLayer:FunctionalTesting",
)


CORESANDBOX_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        CORESANDBOX_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="PloneVoltoCoreSandboxLayer:AcceptanceTesting",
)


class PloneVoltoMigrationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.volto)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])


MIGRATION_FIXTURE = PloneVoltoMigrationLayer()


MIGRATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MIGRATION_FIXTURE,),
    name="PloneVoltoMigrationLayer:IntegrationTesting",
)


MIGRATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MIGRATION_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneVoltoMigrationLayer:FunctionalTesting",
)
