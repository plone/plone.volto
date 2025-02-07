from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.interface import implementer


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    def default_metadata_fields(self):
        # Fields to include in the default catalog-based summary
        # serialization in plone.restapi. We try to include everything
        # needed to render useful listings/teasers.
        return {
            "head_title",
            "effective",
            "end",
            "getObjSize",
            "image_field",
            "image_scales",
            "mime_type",
            "nav_title",
            "start",
        }
