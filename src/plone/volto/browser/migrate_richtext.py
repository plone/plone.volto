from logging import getLogger
from operator import itemgetter
from plone import api
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
        self.convert_to_slate = request.get("convert_to_slate", True)

        if not self.request.form.get("form.submitted", False):
            return self.index()

        results = migrate_richtext_to_blocks(
            portal_types=self.portal_types,
            service_url=self.service_url,
            purge_richtext=self.purge_richtext,
            convert_to_slate=self.convert_to_slate,
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
    convert_to_slate=True,
):
    if portal_types is None:
        portal_types = types_with_blocks()
    elif isinstance(portal_types, str):
        portal_types = [portal_types]
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
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

            # use https://github.com/plone/blocks-conversion-tool
            payload = {"html": text}
            if not convert_to_slate:
                payload["converter"] = "draftjs"

            r = requests.post(service_url, headers=headers, json=payload)
            r.raise_for_status()
            slate_data = r.json()
            slate_data = slate_data["data"]

            blocks = {}
            uuids = []

            # add title
            uuid = str(uuid4())
            blocks[uuid] = {"@type": "title"}
            uuids.append(uuid)

            # add description
            if obj.description:
                uuid = str(uuid4())
                blocks[uuid] = {"@type": "description"}
                uuids.append(uuid)

            # TODO: add leadimage block if beahavio is enabled and image exists

            # add slate blocks
            for block in slate_data:
                uuid = str(uuid4())
                uuids.append(uuid)
                blocks[uuid] = block

            obj.blocks = blocks
            obj.blocks_layout = {"items": uuids}
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


def types_with_blocks():
    """A list of content types with volto.blocks behavior"""
    portal_types = api.portal.get_tool("portal_types")
    results = []
    for fti in portal_types.listTypeInfo():
        behaviors = getattr(fti, "behaviors", [])
        if "volto.blocks" in behaviors:
            results.append(fti.id)
    return results
