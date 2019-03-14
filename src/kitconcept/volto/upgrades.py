from plone import api


def do_something(context):
    for brain in api.content.find(portal_type="Event"):
        event = brain.getObject()
        event.reindexObject()
