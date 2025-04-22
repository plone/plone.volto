<p align="center">
    <img alt="Plone Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-logo.png">
</p>

<h1 align="center">plone.volto</h1>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/plone.volto)](https://pypi.org/project/plone.volto/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/plone.volto)](https://pypi.org/project/plone.volto/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/plone.volto)](https://pypi.org/project/plone.volto/)
[![PyPI - License](https://img.shields.io/pypi/l/plone.volto)](https://pypi.org/project/plone.volto/)
[![PyPI - Status](https://img.shields.io/pypi/status/plone.volto)](https://pypi.org/project/plone.volto/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/plone.volto)](https://pypi.org/project/plone.volto/)

[![Meta](https://github.com/plone/plone.volto/actions/workflows/meta.yml/badge.svg)](https://github.com/plone/plone.volto/actions/workflows/meta.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/plone/plone.volto)](https://github.com/plone/plone.volto)
[![GitHub Repo stars](https://img.shields.io/github/stars/plone/plone.volto?style=social)](https://github.com/plone/plone.volto)

</div>

`plone.volto` configures [Plone](https://plone.org/) to work with [Volto](https://www.npmjs.com/package/@plone/volto), the default frontend of Plone since version 6.0.

## Installation

Add `plone.volto` either to the Plone installation using `pip`:

```shell
pip install plone.volto
```

or add it as a dependency in your package's `setup.py`:

```python
    install_requires = [
        "plone.volto",
        "setuptools",
    ],
```

## Compatibility

`plone.volto` version 5.x works with Plone 6.1 (pre-alpha and alpha), and supports Python 3.10, 3.11, and 3.12.

Volto requires specific versions of `plone.volto` and `plone.restapi`:

| `plone.volto` | `Plone` | `plone.restapi` | Comments |
| --- | --- | --- | --- |
|  5.x | 6.1 |  8.41.0 and above | |
|  4.x | 5.2, 6.0 |  8.41.0 and above | |
|  3.x | 5.1, 5.2 |  8.13.0 and above | Requires new `JSONSummarySerializerMetadata` serializer added in `plone.restapi` 8.13.|
|  2.x (`kitconcept.volto`) | 5.1, 5.2 |  7.0.0 and above | New image scales |
|  1.x (`kitconcept.volto`) | 5.1, 5.2 |  6.0.0 and below | New transforms and features |

Volto only supports the latest `plone.restapi` branch, therefore it is recommended to always use the latest version in your Volto projects.

## Plone 6 architecture

Architectural diagram of Plone 6:

```text
    Frontend
    ┌──────────────────────────────┐
    │                              │
    │            Volto             │
    │                              │
    └────────┬────────────┬────────┘
             │            ▲
             │    HTTP    │
    Backend  ▼            │
    ┌────────┴────────────┴────────┐
    │┌────────────────────────────┐│
    ││        plone.restapi       ││
    │└────────────────────────────┘│
    │┌────────────────────────────┐│
    ││         plone.volto        ││
    │└────────────────────────────┘│
    │┌────────────┐ ┌─────────────┐│
    ││ Plone Core │ │   Add-Ons   ││
    │└────────────┘ └─────────────┘│
    └──────────────────────────────┘
```

## Features

`plone.volto` provides the following features:


### Volto blocks support


`plone.volto` enables the new Volto blocks editor on `Document`, `Language Root Folder`, and `Site Root`.


### Block types index

`plone.volto` adds a `block_types` index to the Plone catalog.
It can be used to query for items that use a particular type of block.

```python
from plone import api
portal_catalog = api.portal.get_tool("portal_catalog")
portal_catalog.searchResults(block_types="image")
```

The `block_types` index was added in `plone.volto` 4.1.0.
By default it is only added for new Plone sites.
To add it to an existing site, run `plone.volto.upgrades.add_block_types_index` manually.


### Multilingual support

`plone.volto` supports multilingual websites.
Install PAM before installing this package, and a Language Root Folder  will be created in each enabled language.
Support is currently only for `EN` and `DE`.

### Document content type

`plone.volto` disables the `Richtext` and `Table of Contents` behaviors for the `Document` content type.
Rich text functionality is provided by the new Volto blocks editor.
The `Table of Contents` functionality is provided by the `Table of Contents` block in Volto.


### CORS profile

A quick helper to enable CORS for development configuration is also provided in the
`plone.volto` module. You can call:

```xml
<include package="plone.volto.cors" />
```

from your ZCML while developing.

Enable it on demand, since it's considered a security issue if you enable CORS in your
productions sites.

It's planned that Volto will feature a development pass-through proxy to the backend in
the future. It will be addressed in next sprints.

### ZLog patch

`plone.restapi` low level errors are routed through the ancient ZLog and are `plone_error`
enabled, making it difficult to follow since all are marked with a UUID, specifically when
using helpers like Sentry. This patch removes the UUID so the same error is categorized
all together. This is planned to be addressed in next sprints.


### Patch for `subject` field

There are some problems of serialization on special characters derived from the
current shape of the Plone's default Dexterity `subjects` field that have to be
addressed in order to make it work properly with Volto (and other systems that are not
Plone). This will be fixed in core in upcoming sprints.


### Preview image behavior

The preview image behavior makes content types provide a `preview_image` field that can store a preview image that Volto views can pick up.
This is especially useful for listings (e.g. listing block customizations) and teaser elements (e.g. teaser blocks).

The `volto.preview_image` behavior can be enabled in the generic setup XML definition of a content type (e.g. `/profiles/default/types/MyContentType.xml`):

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<object i18n:domain="my.project" meta_type="Dexterity FTI" name="MyContentType"
  xmlns:i18n="http://xml.zope.org/namespaces/i18n">

  ...

  <!-- Enabled behaviors -->
  <property name="behaviors" purge="false">
    ...
    <element value="volto.preview_image" />
  </property>
  ...
</object>
```

There is also another variation of the preview image behavior called `volto.preview_image_link`.
This one stores preview images using a relation to an image content type, rather than in an image field. This might be preferable if many content items use the same preview image.

### Navigation title behavior

The navigation title makes content types provide a `nav_title` field that is used by Volto in the main navigation, the breadcrumbs, and the navigation portlet.

The `volto.navtitle` behavior can be enabled in the generic setup XML definition of a content type, for example in `/profiles/default/types/MyContentType.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<object i18n:domain="my.project" meta_type="Dexterity FTI" name="MyContentType"
  xmlns:i18n="http://xml.zope.org/namespaces/i18n">

  ...

  <!-- Enabled behaviors -->
  <property name="behaviors" purge="false">
    ...
    <element value="volto.navtitle" />
  </property>
  ...
</object>
```

### Kicker behavior

The `volto.kicker` behavior adds a Kicker field that can be used to display a line of text above the title.

(The internal name of the field is `head_title`, for backwards-compatibility reasons.)

This behavior can be enabled in the generic setup XML definition of a content type, for example in `/profiles/default/types/MyContentType.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<object i18n:domain="my.project" meta_type="Dexterity FTI" name="MyContentType"
  xmlns:i18n="http://xml.zope.org/namespaces/i18n">

  ...

  <!-- Enabled behaviors -->
  <property name="behaviors" purge="false">
    ...
    <element value="volto.kicker" />
  </property>
  ...
</object>
```

> [!NOTE]
> The previous name of this behavior, `volto.head_title`, was deprecated in `plone.volto` 5.0.

### Image scales

This package introduces new Plone image scales in Plone and redefines a couple of existing ones.
These are know to work well with the Volto layout and grid system:

| Scale | Dimensions |
| --- | --- |
| icon | 32:32 |
| tile | 64:64 |
| thumb | 128:128 |
| mini | 200:65536 |
| preview | 400:65536 |
| teaser | 600:65536 |
| large | 800:65536 |
| larger | 1000:65536 |
| great | 1200:65536 |
| huge | 1600:65536 |

**This change is opinionated and may collide with your previously defined ones, so make sure your add-on's profiles are applied AFTER this one.**


## History

<p align="left">
    <a href="https://kitconcept.com/">
      <img alt="Plone Logo" width="150px" src="https://kitconcept.com/logo.svg" alt="kitconcept GmbH">
    </a>
</p>

The code of `plone.volto` has been under active development and is used in production since 2018.
It was first named `kitconcept.voltodemo` (deprecated since March, 5th 2020), then `kitconcept.volto`.
In September 2021 `kitconcept.volto` was renamed to `plone.volto`, and was contributed to the Plone core as part of [PLIP #2703](https://github.com/plone/Products.CMFPlone/issues/2703).

## This project is supported by

<p align="left">
    <a href="https://plone.org/foundation/">
      <img alt="Plone Logo" width="200px" src="https://raw.githubusercontent.com/plone/.github/main/plone-foundation.png">
    </a>
</p>

## License

The project is licensed under the GPLv2.
