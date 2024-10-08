from plone.registry.interfaces import IRegistry
from plone.rest.interfaces import IAPIRequest
from plone.volto import content
from plone.volto import interfaces
from plone.volto import logger
from plone.volto.bbb import alias_module
from plone.volto.interfaces import IVoltoSettings
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_burst
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_period
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_pool
from zope.component import getUtility

import logging
import os


LOG = logging.getLogger("Zope.SiteErrorLog")

try:
    from collective.folderishtypes.dx import content  # noqa F401
except ImportError:
    logger.info("Aliasing collective.folderish classes to plone.volto classes.")
    alias_module("collective.folderishtypes.dx.content", content)
    alias_module("collective.folderishtypes.dx.interfaces", interfaces)
    alias_module("collective.folderishtypes.interfaces", interfaces)


def _do_copy_to_zlog(self, now, strtype, entry_id, url, tb_text):
    when = _rate_restrict_pool.get(strtype, 0)
    if now > when:
        next_when = max(when, now - _rate_restrict_burst * _rate_restrict_period)
        next_when += _rate_restrict_period
        _rate_restrict_pool[strtype] = next_when

        LOG.error(f"{strtype}: {url}\n{tb_text.rstrip()}")


def construct_url(self, randomstring):
    """Return URL used in registered_nodify_template to allow user to
    change password
    """
    # domain as seen by Plone backend
    frontend_domain = self.portal_state().navigation_root_url()
    if IAPIRequest.providedBy(self.request):
        # the reset was requested through restapi, the frontend might have
        # a different domain. Use volto.frontend_domain in the registry
        # without triggering possible "record not found"
        # Default value for volto.frontend_domain is http://localhost:3000

        # to consider: maybe we should/could override @@portal_state/navigation_root_url() for
        # IAPIRequest to fix this on a higher level

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IVoltoSettings, prefix="volto", check=False)
        settings_frontend_domain = os.environ.get("VOLTO_FRONTEND_DOMAIN") or getattr(
            settings, "frontend_domain", None
        )
        if settings_frontend_domain:
            frontend_domain = settings_frontend_domain
        if frontend_domain.endswith("/"):
            frontend_domain = frontend_domain[:-1]
    return f"{frontend_domain}/passwordreset/{randomstring}"
