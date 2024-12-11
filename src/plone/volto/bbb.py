# flake8: noqa
from types import ModuleType

import sys


# This was copied from plone.app.upgrade
# to avoid a hard dependency on it.
def alias_module(name, target):
    parts = name.split(".")
    i = 0
    module = None
    while i < len(parts) - 1:
        i += 1
        module_name = ".".join(parts[:i])
        try:
            __import__(module_name)
        except ImportError:
            new_module = ModuleType(module_name)
            sys.modules[module_name] = new_module
            if module is not None:
                setattr(module, parts[i - 1], new_module)
        module = sys.modules[module_name]

    setattr(module, parts[-1], target)
    # also make sure sys.modules is updated
    sys.modules[module_name + "." + parts[-1]] = target
