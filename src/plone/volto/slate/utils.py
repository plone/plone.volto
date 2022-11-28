""" utils module """
from collections import deque


def iterate_children(value):
    """iterate_children.

    :param value:
    """
    queue = deque(value)
    while queue:
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])
