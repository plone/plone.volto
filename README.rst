.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============================================================================
kitconcept.volto
==============================================================================

.. image:: https://kitconcept.com/logo.svg
   :alt: kitconcept
   :target: https://kitconcept.com/


.. image:: https://secure.travis-ci.org/collective/kitconcept.volto.png
    :target: http://travis-ci.org/collective/kitconcept.volto

Development
-----------

Requirements:

- Python 2.7
- Virtualenv

Setup::

  make

Run Static Code Analysis::

  make code-Analysis

Run Unit / Integration Tests::

  make test

Run Robot Framework based acceptance tests::

  make test-acceptance
