from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.base.defaultpage import check_default_page_via_view
from plone.base.interfaces import IHideFromBreadcrumbs
from plone.base.interfaces import INavigationRoot
from plone.base.navigationroot import get_navigation_root
from plone.base.utils import pretty_title_or_id
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(INavigationBreadcrumbs)
class PhysicalNavigationBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = aq_parent(context)

        name, item_url = get_view_url(context)
        last_crumb = {
            "absolute_url": item_url,
            "Title": pretty_title_or_id(context, context),
            "nav_title": getattr(aq_base(context), "nav_title", ""),
        }

        if container is None:
            return (last_crumb,)

        # Replicate Products.CMFPlone.browser.navigaton.RootPhysicalNavigationBreadcrumbs.breadcrumbs()
        # cause it is not registered during tests
        if INavigationRoot.providedBy(context):
            return ()

        view = getMultiAdapter((container, request), name="breadcrumbs_view")
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        rootPath = get_navigation_root(context)
        itemPath = "/".join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation
        # root
        if not check_default_page_via_view(
            context, request
        ) and not rootPath.startswith(itemPath):
            base += (last_crumb,)
        return base
