Changelog
=========


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
