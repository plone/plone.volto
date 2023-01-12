.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://img.shields.io/pypi/v/plone.volto.svg
  :target: https://pypi.python.org/pypi/plone.volto

.. image:: https://github.com/plone/plone.volto/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/plone/plone.volto/actions/workflows/tests.yml

==============================================================================
plone.volto
==============================================================================

plone.volto configures Plone to work with `Volto <https://www.npmjs.com/package/@plone/volto>`_, the new default frontend for Plone 6.


Installation
============

Install plone.volto by adding it to your buildout::

    [buildout]
    ...

    [instance]
    ...

    eggs =
        plone.volto
        ...


Compatibility
=============

plone.volto currently works for both Plone 5.2 and Plone 6 (pre-alpha and alpha).
It support Python 3.7, 3.8 and 3.9.

Though, Volto requires specific versions of plone.volto and plone.restapi:

+---------------------------+-----------------------+-------------------------------------------------------------------------------------------------+
|  plone.volto              |  plone.restapi        | Reason                                                                                          |
+---------------------------+-----------------------+-------------------------------------------------------------------------------------------------+
|  3.1.x                    |  8.13.0 and above     | Requires new JSONSummarySerializerMetadata serializer added in plone.restapi 8.13.0             |
+---------------------------+-----------------------+-------------------------------------------------------------------------------------------------+
|  2.x (kitconcept.volto)   |  7.0.0 and above      | New image scales                                                                                |
+---------------------------+-----------------------+-------------------------------------------------------------------------------------------------+
|  1.x (kitconcept.volto)   |  6.0.0 and below      | New transforms and features                                                                     |
+---------------------------+-----------------------+-------------------------------------------------------------------------------------------------+

plone.restapi 7.x.x is included in Plone 5.2.4 (and later).

You can still use 2.x in p.restapi 7.0.0 based installations but the transforms included won't work.

Volto only supports the latest plone.restapi branch, therefore it is recommended to always use the latest version in your Volto projects.

Plone 6 Architecture
====================

Architectural Diagram of Plone 6::

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


Features
========

plone.volto provides the following features:


Volto Blocks Support
--------------------

plone.volto enables the new Volto Blocks editor on ``Document``, ``Language Root Folder`` and ``Site Root``.


Multilingual Support
--------------------

plone.volto supports multilingual websites.
Install PAM before installing this package and demo homepages will be created in each enabled language.
Currently only support for EN/DE.


Volto Blocks for Plone Site Root
--------------------------------

plone.volto contains a hack to make the Plone site Volto blocks-enabled with some demo content.
You can take only the hack to enable the blocks on your site.

You can see it in action in the Volto demo: https://6.demo.plone.org

Install the provided profile to install it by default:

  plone.volto:default-homepage

e.g. in your GS ``metadata.xml`` along with your other dependencies::

  <metadata>
  <version>1000</version>
  <dependencies>
    <dependency>plone.volto:default-homepage</dependency>
  </dependencies>
  </metadata>

**NOTE**: The default block for creating the default content in the root (or
corresponding Language Root Folders) is "draftJS" text block. ``plone.volto`` provides a
profile if you want to create Slate blocks: you need to use the ``default-homepage-slate``
profile.

Document Content Type
---------------------

plone.volto disables the ``Richtext`` and ``Table of Contents`` behaviors for the ``Document`` content type.
Rich Text functionality is provided by the new Volto Blocks editor.
The ``Table of Contents`` functionality is provided by the ``Table of Contents Block`` in Volto.


CORS Profile
------------

A quick helper for enable CORS for development config is also provided in the
``plone.volto`` module. So you can call::

  <include package="plone.volto.cors" />

from your ZCML while developing.

Enable it on demand, since it's considered a security issue if you enable CORS in your
productions sites.

It's planned that Volto will feature a development pass-through proxy to the backend in
the future. It will be addressed in next sprints.

ZLog Patch
----------

p.restapi low level errors are routed through the ancient ZLog and are ``plone_error``
enabled, making it difficult to follow since all are marked with a UUID. Specially if
using helpers like Sentry. This patch removes the UUID so the same error is categorized
all together. This is planned to be addressed in next sprints.


Patch for ``subject`` Field
---------------------------

There are some problems of serialization on special characters derivated from how the
current shape of the Plone's default Dexterity ``subjects`` field that has to be
addressed in order to make it work properly with Volto (and other systems that are not
Plone). This will be fixed in core in upcoming sprints.


Preview Image Behavior
----------------------

The preview image behavior makes content types provide a ``preview_image`` field that can store a preview image that Volto views can pick up.
This is especially userful for listings (e.g. listing block customizations) and teaser elements (e.g. teaser blocks such as [volto-blocks-grid](https://github.com/kitconcept/volto-blocks-grid)).

The ``volto.preview_image`` behavior can be enabled in the generic setup XML definition of a content type (e.g. ``/profiles/default/types/MyContentType.xml``)::

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

There is also another variation of the preview image behavior called ``volto.preview_image_link``.
This one stores preview images using a relation to an Image content type, rather than in an image field. This might be preferable if many content items use the same preview image.

Navigation Title Behavior
-------------------------

The navigation title makes content types provide a nav_title field that is used by Volto in the main navigation, the breadcrumbs and the navigation portlet.

The "volto.navtitle behavior can be enabled in the generic setup XML definition of a content type (e.g. "/profiles/default/types/MyContentType.xml")::

   <?xml version="1.0" encoding="UTF-8" ?>
   <object i18n:domain="fzj.internet" meta_type="Dexterity FTI" name="MyContentType"
     xmlns:i18n="http://xml.zope.org/namespaces/i18n">

     ...

     <!-- Enabled behaviors -->
     <property name="behaviors" purge="false">
       ...
       <element value="volto.navtitle" />
     </property>
     ...
   </object>


Head Title Behavior
-------------------

The headtitle makes content types provide a headtitle field that can be used by Volto in teasers and alikes.

The "volto.head_title" behavior can be enabled in the generic setup XML definition of a content type (e.g. "/profiles/default/types/MyContentType.xml")::

   <?xml version="1.0" encoding="UTF-8" ?>
   <object i18n:domain="fzj.internet" meta_type="Dexterity FTI" name="MyContentType"
     xmlns:i18n="http://xml.zope.org/namespaces/i18n">

     ...

     <!-- Enabled behaviors -->
     <property name="behaviors" purge="false">
       ...
       <element value="volto.head_title" />
     </property>
     ...
   </object>


Image Scales
------------

This package introduces new Plone image scales in Plone and redefines a couple of
existing ones. These are know to work well with Volto layout and grid system::

    icon 32:32
    tile 64:64
    thumb 128:128
    mini 200:65536
    preview 400:65536
    teaser 600:65536
    large 800:65536
    larger 1000:65536
    great 1200:65536
    huge 1600:65536

**This change is opinionated and may collide with your previously defined ones, so make
sure your add-on's profiles are applied AFTER this one.**


Credits and History
-------------------

.. image:: https://kitconcept.com/logo.svg
   :width: 150px
   :alt: kitconcept
   :target: https://kitconcept.com/

The code of plone.volto has been under active development and is used in production since 2018.
First as kitconcept.voltodemo (deprecated since March, 5th 2020), then as kitconcept.volto.
In September 2021 kitconcept.volto has been renamed to plone.volto and has been contributed to the Plone core as part of `PLIP #2703
<https://github.com/plone/Products.CMFPlone/issues/2703>`_.
