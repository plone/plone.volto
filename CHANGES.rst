Changelog
=========


1.7.0 (2021-01-21)
------------------

- Add ``breadcrumbs_view`` override to include ``nav_title``
  [sneridagh]


1.6.0 (2021-01-14)
------------------

- Added indexers for `preview_image`, it allows the Volto object browser widget to access it
  [sneridagh]


1.5.2 (2020-12-14)
------------------

- Missing ZCML for translations
  [sneridagh]


1.5.1 (2020-12-14)
------------------

- Add zest.pocompile
  [sneridagh]

- Add missing .mo
  [sneridagh]


1.5.0 (2020-12-09)
------------------

- Fix locales default in German
  [sneridagh]


1.4.0 (2020-07-29)
------------------

- Add volto.preview_image behavior to Page type.
  [timo]


1.3.2 (2020-05-17)
------------------

- Make sure that the enable_pam helper does its job.
  [sneridagh]


1.3.1 (2020-05-12)
------------------

- Fix LRF global allow and ensure default behaviors
  [sneridagh]


1.3.0 (2020-05-11)
------------------

- Add registry navigation setting for not show the current item in navigations
  [sneridagh]

- New enable_pam setuphandlers helper
  [sneridagh]

- New enable_pam_consistency setuphandlers helper
  [sneridagh]


1.2.0 (2020-04-17)
------------------

- Bring back the event type, since it's fully working in Volto now
  [sneridagh]

- fix typo in behavior name ``navttitle`` -> ``navtitle``
  [sneridagh]


1.1.0 (2020-03-10)
------------------

- Added a specific IImageScaleFactory for ``Image`` content type, to fix SVG handling
  [sneridagh]


1.0.1 (2020-03-08)
------------------

- Update version numbers in default home page.
  [sneridagh]


1.0.0 (2020-03-06)
------------------

- Add Zope log patch
  [sneridagh]

- Add nav_title and preview_image behaviors
  [sneridagh]

- override plone.app.vocabularies.Keywords with a version that
  uses the unencode subject value as the token.
  [csenger]

- Remove versioning behavior from Document type.
  [timo]

- Backport all features that were in kitconcept.voltodemo
  [sneridagh]

- Patch Password reset tool in Products.CMFPlone to use the optional volto_domain in the
  e-email which is sent to users, only if the request is made through REST.
  [fredvd]

- Add Volto settings control panel with frontend_domain field.
  [fredvd]

- Homepage profile for demo purposes
  [sneridagh]

- CORS profile
  [sneridagh]

- Enable Volto Blocks for Document and LRF
  [sneridagh]

- Initial release.
  [kitconcept]
