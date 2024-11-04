from plone.autoform.interfaces import READ_PERMISSIONS_KEY
from plone.autoform.interfaces import WRITE_PERMISSIONS_KEY
from plone.supermodel.interfaces import ISchemaPlugin
from plone.volto.interfaces import ISiteSettingsSchema
from zope.component import adapter
from zope.interface import implementer


# Default permissions for fields in the
# site settings schema
PERMISSIONS = {
    READ_PERMISSIONS_KEY: "zope.Public",
    WRITE_PERMISSIONS_KEY: "cmf.ManagePortal",
}


@adapter(ISiteSettingsSchema)
@implementer(ISchemaPlugin)
class SettingsPermissionsPlugin:
    order = -10

    def __init__(self, schema):
        self.schema = schema

    def _set_permissions(
        self, permission_key: str, permission: str, fieldnames: set[str]
    ):
        value = {fieldname: permission for fieldname in fieldnames}
        self.schema.setTaggedValue(permission_key, value)

    def _get_fields_with_tagged_value(self, permission_key: str) -> set[str]:
        try:
            value = self.schema.getTaggedValue(permission_key)
        except KeyError:
            value = {}
        return {name for name in value}

    def __call__(self):
        self.names = set(self.schema.names())
        # Add permissions annotations to schema
        for permission_key, permission in PERMISSIONS.items():
            exclude_fields = self._get_fields_with_tagged_value(permission_key)
            fieldnames = self.names.difference(exclude_fields)
            self._set_permissions(permission_key, permission, fieldnames)
