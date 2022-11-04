from logging import getLogger
from operator import itemgetter
from plone import api
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.textfield.value import RichTextValue
from Products.Five import BrowserView
from uuid import uuid4
from zope.i18n import translate

import requests
import transaction


logger = getLogger(__name__)


class MigrateRichTextToVoltoBlocks(BrowserView):
    """Form to trigger migrating html from Richxtext fields to slate."""

    def __call__(self):
        request = self.request
        self.service_url = request.get("service_url", "http://localhost:5000/html")
        self.purge_richtext = request.get("purge_richtext", False)
        self.portal_types = request.get("portal_types", [])
        self.portal_types_info = self.types_with_blocks()
        self.slate = request.get("slate", True)

        if not self.request.form.get("form.submitted", False):
            return self.index()

        results = migrate_richtext_to_blocks(
            portal_types=self.portal_types,
            service_url=self.service_url,
            purge_richtext=self.purge_richtext,
            slate=self.slate,
        )
        api.portal.show_message(
            "Migrated {} items from richtext to blocks".format(results),
            request=self.request,
        )
        return self.index()

    def types_with_blocks(self):
        """A list with info on all content types with existing items."""
        catalog = api.portal.get_tool("portal_catalog")
        portal_types = api.portal.get_tool("portal_types")
        results = []
        for fti in portal_types.listTypeInfo():
            behaviors = getattr(fti, "behaviors", [])
            if "volto.blocks" not in behaviors:
                continue
            number = len(catalog.unrestrictedSearchResults(portal_type=fti.id))
            if number >= 1:
                results.append(
                    {
                        "number": number,
                        "value": fti.id,
                        "title": translate(
                            fti.title, domain="plone", context=self.request
                        ),
                    }
                )
        return sorted(results, key=itemgetter("title"))


def migrate_richtext_to_blocks(
    portal_types=None,
    service_url="http://localhost:5000/html",
    fieldname="text",
    purge_richtext=False,
    slate=True,
):
    if portal_types is None:
        portal_types = types_with_blocks()
    elif isinstance(portal_types, str):
        portal_types = [portal_types]
    results = 0
    for portal_type in portal_types:
        for index, brain in enumerate(
            api.content.find(portal_type=portal_type, sort_on="path"), start=1
        ):
            obj = brain.getObject()
            text = getattr(obj.aq_base, fieldname, None)
            if not text:
                continue
            if isinstance(text, RichTextValue):
                text = text.raw
            if not text or not text.strip():
                continue

            blocks = {}
            blocks_layout = {"items": []}

            # add title block
            uuid = str(uuid4())
            blocks[uuid] = {"@type": "title"}
            blocks_layout["items"].append(uuid)

            # add description block
            if obj.description:
                uuid = str(uuid4())
                blocks[uuid] = {"@type": "description"}
                blocks_layout["items"].append(uuid)

            if ILeadImage(obj, None) and ILeadImage(obj).image:
                uuid = str(uuid4())
                blocks[uuid] = {"@type": "leadimage"}
                blocks_layout["items"].append(uuid)

            text_blocks, text_uuids = get_blocks_from_richtext(
                text,
                service_url=service_url,
                slate=slate,
            )
            blocks.update(text_blocks)
            blocks_layout["items"] += text_uuids

            obj.blocks = blocks
            obj.blocks_layout = blocks_layout
            obj._p_changed = True

            if purge_richtext:
                setattr(obj, fieldname, None)

            obj.reindexObject(idxs=["SearchableText"])
            results += 1
            logger.debug(f"Migrated richtext to blocks for: {obj.absolute_url()}")

            if not index % 1000:
                logger.info(f"Commiting after {index} items...")
                transaction.commit()
        msg = f"Migrated {index} {portal_type} to blocks"
        logger.info(msg)
    return results


def get_blocks_from_richtext(
    text,
    service_url="http://localhost:5000/html",
    slate=True,
):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"html": text}
    if not slate:
        payload["converter"] = "draftjs"
    r = requests.post(service_url, headers=headers, json=payload)
    r.raise_for_status()
    slate_data = r.json()
    slate_data = slate_data["data"]
    blocks = {}
    uuids = []
    # generate slate blocks
    for block in slate_data:
        uuid = str(uuid4())
        uuids.append(uuid)
        blocks[uuid] = block
    return blocks, uuids


def types_with_blocks():
    """A list of content types with volto.blocks behavior"""
    portal_types = api.portal.get_tool("portal_types")
    results = []
    for fti in portal_types.listTypeInfo():
        behaviors = getattr(fti, "behaviors", [])
        if "volto.blocks" in behaviors:
            results.append(fti.id)
    return results
