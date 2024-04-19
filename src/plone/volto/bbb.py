# flake8: noqa

try:
    from plone.base.interfaces import IPloneSiteRoot
except ImportError:
    from Products.CMFPlone.interfaces import IPloneSiteRoot
