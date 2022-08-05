from plone.app.querystring.queryparser import getPathByUID


def _objectbrowserReference(context, row):
    """
    We expect row.values to be something like this:

    {
        "object": {
            "UID": "123456789",
            "Title": "Foo",
            "path": "/foo"
        },
        "depth": 1

    }
    """

    values = row.values
    if not isinstance(values, dict):
        return {}
    obj = values.get("object", {})
    depth = values.get("depth", None)
    if not obj or not obj.get("UID", None):
        return {}
    values = getPathByUID(context, obj["UID"])

    query = {}
    if depth is not None:
        query["depth"] = depth
        # when a depth value is specified, a trailing slash matters on the
        # query
        values = values.rstrip("/")
    query["query"] = [values]
    return {row.index: query}
