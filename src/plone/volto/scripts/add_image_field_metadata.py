"""
bin/instance -O Plone run scripts/add_image_field_metadata.py
"""
from plone import api
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.volto.behaviors.preview import IPreview
from plone.volto.scripts.utils import print_info
import transaction


catalog = api.portal.get_tool("portal_catalog")

with api.env.adopt_roles(["Manager"]):
    images = api.content.find(object_provides=ILeadImageBehavior.__identifier__)
    preview_images = api.content.find(object_provides=IPreview.__identifier__)

    brains = images + preview_images

    for brain in brains:
        obj = brain.getObject()
        catalog.catalog_object(obj)
        print_info(f"Recataloging object: {brain.getPath()}")

transaction.commit()
