"""Init and utils."""
from zope.i18nmessageid import MessageFactory

import logging


PROJECTNAME = "plone.volto"
_ = MessageFactory(PROJECTNAME)
logger = logging.getLogger(PROJECTNAME)
config = {}
