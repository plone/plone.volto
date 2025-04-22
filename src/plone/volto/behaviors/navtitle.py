from plone.app.dexterity import _ as _P
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from plone.volto import _
from zope.interface import provider
from zope.schema import TextLine


@provider(IFormFieldProvider)
class INavTitle(model.Schema):

    model.fieldset("settings", label=_P("Settings"), fields=["nav_title"])

    nav_title = TextLine(title=_("Navigation title"), required=False)
