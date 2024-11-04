from plone.supermodel import model
from plone.volto.interfaces import ISiteSettingsSchema
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISiteSettingsSchema)
class SettingsSchemaClass(model.SchemaClass):
    pass


SettingsSchema = SettingsSchemaClass(
    "SettingsSchema",
    (Interface,),
    __module__="plone.volto.sitesettings",
)


def finalizeSettingsSchemas(parent=SettingsSchema):
    """Finalize schemas inheriting from SettingsSchema."""
    model.finalizeSchemas(parent)
