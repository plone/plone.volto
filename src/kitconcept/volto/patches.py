from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_pool
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_burst
from Products.SiteErrorLog.SiteErrorLog import _rate_restrict_period

import logging

LOG = logging.getLogger("Zope.SiteErrorLog")


def _do_copy_to_zlog(self, now, strtype, entry_id, url, tb_text):
    when = _rate_restrict_pool.get(strtype, 0)
    if now > when:
        next_when = max(when, now - _rate_restrict_burst * _rate_restrict_period)
        next_when += _rate_restrict_period
        _rate_restrict_pool[strtype] = next_when

        LOG.error("%s: %s\n%s" % (strtype, url, tb_text.rstrip()))
