from collections.abc import Generator
from contextlib import contextmanager
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.autologin import AutoLogin
from plone.app.robotframework.content import Content
from plone.app.robotframework.genericsetup import GenericSetup
from plone.app.robotframework.i18n import I18N
from plone.app.robotframework.mailhost import MockMailHost
from plone.app.robotframework.quickinstaller import QuickInstaller
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework.server import Zope2ServerRemote
from plone.app.robotframework.users import Users
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import helpers as pat_helpers
from plone.app.testing import IntegrationTesting
from plone.app.testing import layers as pat_layers
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.distribution.testing.layer import PloneDistributionFixture
from plone.testing import Layer
from plone.testing import zope

import plone.app.caching  # noQA
import plone.app.discussion  # noQA
import plone.app.iterate  # noQA
import plone.app.multilingual  # noQA
import plone.app.upgrade  # noQA
import plone.volto  # noQA
import plone.volto.coresandbox  # noQA
import Products.CMFPlacefulWorkflow  # noQA


# Each fixture stack creates its own site, with its own id, so that the core,
# coresandbox and migration layers can all stay set up at the same time. The
# migration stack is based on the stock PLONE_FIXTURE, which always creates
# "plone".
CORE_SITE_ID = "volto"
CORESANDBOX_SITE_ID = "coresandbox"
MIGRATION_SITE_ID = "plone"


ANSWERS = {
    "site_id": CORE_SITE_ID,
    "title": "Plone Site",
    "description": "A Plone Site with Volto",
    "site_logo": "name=teste;data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==",  # noQA
    "default_language": "en",
    "portal_timezone": "America/Sao_Paulo",
    "setup_content": True,
}


@contextmanager
def plone_site_id(site_id: str) -> Generator[None]:
    """Make plone.app.testing use ``site_id`` as the Plone site id.

    plone.app.testing looks the site up as ``app[PLONE_SITE_ID]`` in its
    layers and helpers, with ``PLONE_SITE_ID`` fixed to ``"plone"``. This
    swaps the module-level value for the duration of the block.

    :param site_id: The id of the Plone site to use.
    """
    previous = (pat_helpers.PLONE_SITE_ID, pat_layers.PLONE_SITE_ID)
    pat_helpers.PLONE_SITE_ID = pat_layers.PLONE_SITE_ID = site_id
    try:
        yield
    finally:
        pat_helpers.PLONE_SITE_ID, pat_layers.PLONE_SITE_ID = previous


class SiteIdMixin(Layer):
    """Run a layer's set up and tear down hooks against ``site_id``."""

    site_id: str = MIGRATION_SITE_ID

    def setUp(self):
        with plone_site_id(self.site_id):
            super().setUp()

    def tearDown(self):
        with plone_site_id(self.site_id):
            super().tearDown()

    def testSetUp(self):
        with plone_site_id(self.site_id):
            super().testSetUp()

    def testTearDown(self):
        with plone_site_id(self.site_id):
            super().testTearDown()


class SiteIntegrationTesting(SiteIdMixin, IntegrationTesting):
    """``IntegrationTesting`` for the Plone site with id ``site_id``."""

    def __init__(self, site_id: str, bases: tuple, name: str):
        self.site_id = site_id
        super().__init__(bases=bases, name=name, module=__name__)


class SiteFunctionalTesting(SiteIdMixin, FunctionalTesting):
    """``FunctionalTesting`` for the Plone site with id ``site_id``."""

    def __init__(self, site_id: str, bases: tuple, name: str):
        self.site_id = site_id
        super().__init__(bases=bases, name=name, module=__name__)


class BaseFixture(PloneDistributionFixture):
    PACKAGE_NAME = "plone.volto"
    SITES = (("volto", ANSWERS),)
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


# plone.app.robotframework's REMOTE_LIBRARY_BUNDLE_FIXTURE is based on
# PLONE_FIXTURE, which creates its own "plone" site. The bundle only attaches a
# "RobotRemote" attribute to the PloneSite class, shared by every site, so one
# bundle on Startup serves the core and coresandbox sites alike.
REMOTE_LIBRARY_BUNDLE_FIXTURE = RemoteLibraryLayer(
    bases=(zope.STARTUP,),
    libraries=(
        AutoLogin,
        QuickInstaller,
        GenericSetup,
        Content,
        Users,
        I18N,
        MockMailHost,
        Zope2ServerRemote,
    ),
    name="PloneVolto:RobotRemote",
)


class PloneVoltoCoreLayer(SiteIdMixin, PloneSandboxLayer):

    defaultBases = (BASE_FIXTURE,)
    site_id = CORE_SITE_ID


PLONE_VOLTO_CORE_FIXTURE = PloneVoltoCoreLayer()


PLONE_VOLTO_CORE_INTEGRATION_TESTING = SiteIntegrationTesting(
    site_id=CORE_SITE_ID,
    bases=(PLONE_VOLTO_CORE_FIXTURE,),
    name="PloneVoltoCoreLayer:IntegrationTesting",
)


PLONE_VOLTO_CORE_FUNCTIONAL_TESTING = SiteFunctionalTesting(
    site_id=CORE_SITE_ID,
    bases=(PLONE_VOLTO_CORE_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneVoltoCoreLayer:FunctionalTesting",
)


PLONE_VOLTO_CORE_ACCEPTANCE_TESTING = SiteFunctionalTesting(
    site_id=CORE_SITE_ID,
    bases=(
        PLONE_VOLTO_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        zope.WSGI_SERVER_FIXTURE,
    ),
    name="PloneVoltoCoreLayer:AcceptanceTesting",
)


class SandboxFixture(BaseFixture):
    SITES = (("volto", {**ANSWERS, "site_id": CORESANDBOX_SITE_ID}),)
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


class PloneVoltoCoreSandboxLayer(SiteIdMixin, PloneSandboxLayer):

    defaultBases = (SANDBOX_FIXTURE,)
    site_id = CORESANDBOX_SITE_ID

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.volto:coresandbox")


PLONE_VOLTO_CORESANDBOX_FIXTURE = PloneVoltoCoreSandboxLayer()


PLONE_VOLTO_CORESANDBOX_INTEGRATION_TESTING = SiteIntegrationTesting(
    site_id=CORESANDBOX_SITE_ID,
    bases=(PLONE_VOLTO_CORESANDBOX_FIXTURE,),
    name="PloneVoltoCoreSandboxLayer:IntegrationTesting",
)


PLONE_VOLTO_CORESANDBOX_FUNCTIONAL_TESTING = SiteFunctionalTesting(
    site_id=CORESANDBOX_SITE_ID,
    bases=(PLONE_VOLTO_CORESANDBOX_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneVoltoCoreSandboxLayer:FunctionalTesting",
)


PLONE_VOLTO_CORESANDBOX_ACCEPTANCE_TESTING = SiteFunctionalTesting(
    site_id=CORESANDBOX_SITE_ID,
    bases=(
        PLONE_VOLTO_CORESANDBOX_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        zope.WSGI_SERVER_FIXTURE,
    ),
    name="PloneVoltoCoreSandboxLayer:AcceptanceTesting",
)


class PloneVoltoMigrationLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=plone.volto)

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ["Manager"])


PLONE_VOLTO_MIGRATION_FIXTURE = PloneVoltoMigrationLayer()


PLONE_VOLTO_MIGRATION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_VOLTO_MIGRATION_FIXTURE,),
    name="PloneVoltoMigrationLayer:IntegrationTesting",
)


PLONE_VOLTO_MIGRATION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_VOLTO_MIGRATION_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneVoltoMigrationLayer:FunctionalTesting",
)
