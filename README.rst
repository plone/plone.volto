.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
kitconcept.volto
==============================================================================

.. image:: https://kitconcept.com/logo.svg
   :alt: kitconcept
   :target: https://kitconcept.com/


.. image:: https://github.com/kitconcept/kitconcept.volto/workflows/Basic%20tests/badge.svg
    :target: https://github.com/kitconcept/kitconcept.volto/actions?query=workflow%3A%22Basic+tests%22

kitconcept.volto is a helper package to setup a Plone site ready to use with Volto. It
installs several convenience packages, Plone configuration and patches to prepare Plone
to be ready for support all the Volto features. Drop it in your buildout and then
install it. It is used in Volto development itself for testing it.

If you want, take it as base of your own integration package.

Usage
=====

https://github.com/plone/volto/blob/master/api/base.cfg#L13

and along with plonesite recipe:

https://github.com/plone/volto/blob/master/api/base.cfg#L13

Features
========

kitconcept.volto provides the following features:

Demo home page and Plone site blocks support
--------------------------------------------

It features a hack to make the Plone site Volto blocks-enabled with some demo
content. You can take only the hack to enable the blocks on your site.

You can see it in action in the Volto demo: https://volto.kitconcept.com

Install the provided profile to install it by default:

  kitconcept.volto:default-homepage

e.g. in your GS ``metadata.xml`` along with your other dependencies::

  <metadata>
  <version>1000</version>
  <dependencies>
    <dependency>kitconcept.volto:default-homepage</dependency>
  </dependencies>
  </metadata>

Volto Pastanaga Editor
-----------------------

It enables the Volto Blocks behavior on the ``Document`` content type by
default, enabling Volto editor for that content type.

Just use the same pattern to enable your own content types to have blocks.

Document content type
---------------------

``Richtext`` and ``table of contents`` behaviors has been removed from the ``Document``
behaviors since it's confusing for the users if they shows in the form. Both have been
superseeded by blocks in the editor.

CORS profile
------------

A quick helper for enable CORS for development config is also provided in the
``kitconcept.volto`` module. So you can call::

  <include package="kitconcept.volto.cors" />

from your ZCML while developing.

Enable it on demand, since it's considered a security issue if you enable CORS in your
productions sites.

It's planned that Volto will feature a development pass-through proxy to the backend in
the future. It will be addressed in next sprints.

ZLog patch
----------

p.restapi low level errors are routed through the ancient ZLog and are ``plone_error``
enabled, making it difficult to follow since all are marked with a UUID. Specially if
using helpers like Sentry. This patch removes the UUID so the same error is categorized
all together. This is planned to be addressed in next sprints.

Patch fix for Plone ``subject`` field
-------------------------------------

There are some problems of serialization on special characters derivated from how the
current shape of the Plone's default Dexterity ``subjects`` field that has to be
addressed in order to make it work properly with Volto (and other systems that are not
Plone). This will be fixed in core in upcoming sprints.

Support behaviors
-----------------

Some behaviors that have proven to be complementary to Volto views. ``preview_image`` an
image for listings and teasers (different than a lead image). ``nav_title`` a field to
store titles used in navigation components, teasers or doormats.

nav_title in breadcrumbs
------------------------

The support behavior ``nav_title`` has been added to the list of attributes that
``breadcrumbs_view`` is returning, this is done via a customized layered view on
``breadcrumbs_view`` browser view.

Volto blocks enabled LRF
------------------------

Multilingual support for LRF (Language Root Folders) is supported. Install PAM before
installing this package and demo homepages will be created in each enabled language.
Currently only support for EN/DE.

Versions compatibility
----------------------

kitconcept.voltodemo is deprecated in favor of this package as of since March, 5th 2020.
