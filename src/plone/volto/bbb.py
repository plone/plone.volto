# flake8: noqa

try:
    from plone.base.interfaces import IPloneSiteRoot
except ImportError:
    from Products.CMFPlone.interfaces import IPloneSiteRoot

try:
    from plone.base.utils import get_installer
except ImportError:
    from Products.CMFPlone.utils import get_installer
