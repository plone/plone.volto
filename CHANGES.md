# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 5.1.0 (2025-05-07)


### New features:

- Enable automatic versioning for content types with blocks. @davisagli #191
- Enable preview image link behavior by default for most content types. @davisagli #191
- Put preview image fields in their own fieldset, and the navigation title field in the Settings fieldset. @davisagli #191
- Enable navigation title by default for most content types. @ana-oprea #191


### Bug fixes:

- Update `image_scales` in catalog for items with a `preview_image_link` if the image is edited. @davisagli #192


### Internal:

- Don't depend on zest.releaser.
  [thet] 

## 5.0.4 (2025-03-13)


### Bug fixes:

- Resolve UID-based internal links in navigation tabs. @ichim-david #159
- Replace `pkg_resources` with `importlib.metadata` @gforcada #4126

## 5.0.3 (2025-02-11)


### Bug fixes:

- Include `effective`, `end`, `getObjSize`, `mime_type`, and `start` in default summary serialization. @davisagli #184

## 5.0.2 (2025-01-27)


### Bug fixes:

- Implement a specific robots.txt for Volto sites.
  There is an upgrade step which will update the existing plone.robots_txt registry setting unless it has been customized.
  @ericof #178
- Add nav_title and head_title to the default summary serializer metadata fields. @davisagli #181
- Fix DeprecationWarnings. [maurits] #4090

## 5.0.1 (2024-12-17)


### Bug fixes:

- Allow setting `preview_image_link` to an image from a different language root folder. @davisagli #172

## 5.0.0 (2024-12-12)


### Bug fixes:

- Enable the `plone.versioning` behavior for the Page content type. @davisagli #143
- Remove override of Plone's `plone.app.vocabularies.Keywords` vocabulary. @davisagli #157
- The `volto.head_title` behavior has been renamed to `volto.kicker`.
  The old name still works, but is deprecated.
  Content types should be updated to use the new name.
  @iRohitSingh, @davisagli #164
- Don't exclude Plone Site from search results. @davisagli #165
- Fix plone.app.multilingual dependency to be a dependency for tests only. @davisagli #168


### Internal:

- Fix deprecated imports. @petschki #128
- Remove unused ZCML conditions. @davisagli #167

## 5.0.0b2 (2024-11-25)


### Bug fixes:

- Rename `default` distribution to `volto`. @davisagli #161

## 5.0.0b1 (2024-10-30)


### Breaking changes:

- Drop support for Plone 5.2 and Plone 6.0 [@ericof] #155
- The following GenericSetup profiles were removed: `default-homepage`,
  `default-homepage-drafjs`, `default-homepage-slate`, `demo` and `richtext`. @davisagli #155


### New features:

- This package now contains a Plone distribution named "default". @ericof #155


### Internal:

- setup.py: specify the encoding, otherwise it fails on Windows.
  [maurits] 

## 4.4.3 (2024-08-01)

Bug fixes:


- Fix getting the the variation when migrating collections to listing blocks. @pbauer (#158)


## 4.4.2 (2024-06-26)

### Bug fixes:


- Remove runtime dependency on plone.app.upgrade. [@davisagli] (#142)
- Do not fail on startup when the ``requests`` library is missing.
  Conditionally load the views to migrate to Volto: only when the ``requests`` library is available.
  We don't want to make this a hard dependency.
  If you need the migration views, you should include the ``requests`` package yourself.
  [@maurits] (#152)


## 4.4.1 (2024-05-16)

### Bug fixes:


- Do not set the nonfolderish_tabs registry to False. @wesleybl (#145)
- Fix for preview_image_link image_scales adapter when the field is empty.
  Swap condition for `image_field` indexer, `preview_image_link` first, then the default `preview_image`
  [@sneridagh] (#148)


## 4.4.0 (2024-04-25)

### New features:


- Import ILanguageSchema from plone.i18n.interfaces instead of Products.CMFPlone.interfaces.controlpanel. @ksuess
  profile "plone.volto:multilingual": Add language german. @ksuess (#144)


### Bug fixes:


- Avoid a deprecated import warnings in Plone 6. @davisagli (#147)


## 4.3.0 (2024-01-30)

### New features:


- Add `VOLTO_FRONTEND_DOMAIN` as env var for `volto.frontend_domain` registry setting
  [@sneridagh] (#139)


## 4.2.1 (2024-01-26)

### Bug fixes:


- Fix changed behavior and marker interfaces for plone.leadimage and plone.richtext.
  See: https://github.com/plone/plone.app.contenttypes/pull/480
  @thet (#133)
- Avoid accidental acquisition in ``block_types`` indexer. @davisagli (#137)


## 4.2.0 (2023-12-13)

### New features:


- Add pt_BR translations. @wesleybl (#133)
- Add `preview_image_link` behavior to the Example content type for testing @sneridagh (#136)


### Bug fixes:


- Add guard for template used in the Volto installed status message that is Plone 6 only @sneridagh (#135)


## 4.1.0 (2023-08-07)

### New features:


- Add `block_types` index to zcatalog. By default it is only added for new Plone sites.
  To add it to an existing site, run `plone.volto.upgrades.add_block_types_index` manually.
  [margaridasp, davisagli] (#4778)


### Bug fixes:


- Change the implementation for finding nested blocks to use an IBlockVisitor adapter. @davisagli (#127)
- Fix missing translations for head_title field. @davisagli (#130)


## 4.0.10 (2023-07-14)

### Bug fixes:


- Use the plone.app.multilingual conditionally so as is not an explicit dependency
  [@foxtrot-01] (#119)


## 4.0.9 (2023-06-22)

### Bug fixes:


- Let the migration-form @@migrate_to_volto transform richtext to slate-blocks by default.
  [@pbauer] (#122)
- Fix value of unchecked checkboxes in migrate_to_volto.
  [@pbauer] (#124)


## 4.0.8 (2023-03-23)

### Bug fixes:


- Use correct service_url when calling make_document. Fix #95
  [@pbauer] (#95)
- Change home page more demo link. Fix #114 (#114)


## 4.0.7 (2023-03-02)

### Bug fixes:


- Better migration of collections: Fix migrating sort_order. Adapt relative path of query when migrating default-page collection to listing block.
  [@pbauer] (#111)


## 4.0.6 (2023-02-27)

### Bug fixes:


- Prevent AttributeError when migrating to FolderishDocument.
  [@pbauer] (#109)


## 4.0.5 (2023-01-19)

### Bug fixes:


- Include internal links from nested blocks in link integrity recordkeeping. [@davisagli] (#108)


### Internal:


- Update default Plone Classic UI message to inform developers to install, start, and visit the Volto frontend, if desired, with updated links to relevant docs. [@stevepiercy] (#107)


## 4.0.4 (2022-12-16)

### Bug fixes:


- Clarifications in the @@migrate_to_volto wizard. Volto is a separate service that needs to be configured and hosted. It is not included in the Plone backend.
  Editing the main content that was in RichText fields before will no longer be possible after migration.
  Fix link to Volto frontend documentation.
  [fredvd, stevepiercy] (#106)


## 4.0.3 (2022-12-14)

### Bug fixes:


- Fix a11y problems in both demo and default pages @sneridagh (#105)


## 4.0.2 (2022-12-12)

### Bug fixes:


- Fix create default homepage script problem with non existent description field. Fix default and demo page texts
  [@sneridagh] (#103)


## 4.0.1 (2022-12-12)

### Internal:


- Prepare 6 final default text for demo and local installs. [@stevepiercy] (#102)


## 4.0.0 (2022-11-18)

### Internal:


- Re-release plone.volto 4.0.0a15 as 4.0.0 [@tisto] (#99)


## 4.0.0a15 (2022-11-16)

### Bug fixes:


- Fix adding a leadimage block during migration to Volto when a leadimage exists. [@pbauer] (#96)
- Make the `migrate_to_volto` process more robust when running multiple times or when plone.volto was installed first. [@pbauer] (#97)
- Don't acquire nav_title from parent in breadcrumbs view. [@davisagli] (#98)


## 4.0.0a14 (2022-11-02)

### Bug fixes:


- Improve help text for head_title field. [@davisagli] (#92)
- Adjust Plone site actions to work in Volto. [nileshgulia1, davisagli] (#93)
- Show a warning in the classic UI when plone.volto is installed. Fix https://github.com/plone/Products.CMFPlone/issues/3664 [@pbauer] (#94)


## 4.0.0a13 (2022-09-29)

### Bug fixes:


- Keep folder order when migrating from folderishtypes [@cekk] (#86)
- Fix hasPreviewImage and image_field indexers when the preview_image_link relation is broken. [@davisagli] (#91)


## 4.0.0a12 (2022-09-27)

### New features:


- Add proper icon in classic control panel
  [@sneridagh] (#89)


## 4.0.0a11 (2022-09-04)

### Bug fixes:


- Update demo homepage content for Slate, round 2. @stevepiercy (#85)


### Internal:


- Sign CONTRIBUTORS.rst. @stevepiercy (#88)


## 4.0.0a10 (2022-08-30)

### Bug fixes:


- Update default homepage content for Slate. @stevepiercy (#84)


### Internal:


- Added `make i18n` command [@davisagli] (#81)


## 4.0.0a9 (2022-08-12)

### New features:


- Added preview image link behavior (Plone 6+ only)
  [@robgietema] (#49)


## 4.0.0a8 (2022-08-04)

### New features:


- Add better implementation of the PLONE6 check (cosmetic)
  [@sneridagh] (#59)
- Use slate as default text block in default contents for ``default-homepage`` and
  ``multilingual`` profile.
  [@sneridagh] (#77)


## 4.0.0a7 (2022-07-22)

### New features:


- Use new metadata utility for adding the ``image_scales`` to the default serialization.
  [@ericof] (#74)


### Bug fixes:


- Use plone/code-analysis-action on GitHub Actions and plone/code-quality Docker image and versions to format code.
  [@ericof] (#68)
- Fix the handler for resolving UIDs in nested blocks to avoid trying to resolve them twice. This also makes it possible to use deserialization and serialization transforms that intentionally run before the resolveuid transform in the context of nested blocks.
  [@davisagli] (#76)


## 4.0.0a6 (2022-06-25)

### Bug fixes:


- Re-release 4.0.0a5/4.0.0a5.dev0
  [@tisto] (#72)


## 4.0.0a5 (2022-06-25)

### New features:


- Add form ``@@migrate_richtext`` to migrate ``html-richtext`` to slate blocks or draftjs blocks
  [@pbauer] (#47)
- Add ``@@migrate_to_volto`` to prepare existing sites for Volto.
  [@pbauer] (#55)


### Bug fixes:


- Update test to 6.0.0a4 and new pip practices.
  [@sneridagh] (#51)
- Conditional custom ``IImageScaleFactory`` adapter for Plone < 6 (svg are now handled in `plone.namedfile <https://github.com/plone/plone.namedfile/commit/b4f80204759703aa812d1db35589cd92e89ea108>`_).
  [@cekk] (#60)
- Fixed code quality configuration.
  Removed unused imports and variables and sorted the imports.
  [@maurits] (#71)


## 4.0.0a4 (2022-04-08)

- Fix deprecated import of isDefaultPage
  [@pbauer]


## 4.0.0a3 (2022-02-04)

- Fix Multilingual profile, revert to use draftJS (until slate is integrated into Volto)
  [@sneridagh]


## 4.0.0a2 (2022-01-25)

- Bring back the draftJS as default, until Slate is integrated in full in Volto
  [@sneridagh]


## 4.0.0a1 (2022-01-25)

### Breaking

- Use Slate blocks for the default pages
  [@sneridagh]

- Add ``volto.blocks`` behavior to Plone Site GS types info.
  [@sneridagh]

- Remove ``Collection`` from types in GS types info.
  [@sneridagh]

- Remove ``plone.richtext`` behavior from Plone Site, Document, News Item, Events
  [@sneridagh]

- Add blocks behavior on Event and NewsItem
  [@nzambello]

- Add preview_image to Event
  [@nzambello]

### Internal:

- Code cleanup, remove some outdated and unused helpers in ``setuptools.py``
  [@sneridagh]

- Workaround a test fixture isolation issue with the `IVoltoSettings.frontend_domain`
  setting.
  [@rpatterson]


## 3.1.0a9 (2022-01-15)

### Breaking

- Remove c.folderishtypes dependency

### New Feature

- Add new field in the coresandbox: not constrained by vocabulary field but the vocabulary defined in the widget.
  [@sneridagh]


## 3.1.0a8 (2022-01-12)

- Computed copyright dates for content demo pages
  [@sneridagh]

## 3.1.0a7 (2021-12-11)

### New Feature

- Added coresandbox fixture for Volto's cypress tests
  [@sneridagh]

### Internal:

- Test with Plone 6.0.0a2
  [@ericof]


## 3.1.0a6 (2021-11-22)

### New Feature

- Add Basque and Spanish translations
  [@erral]

- Add Italian translations
  [@cekk]

### Bugfix

- Update German translations
  [@timo]

- Fix translation files
  [cekk, timo]


## 3.1.0a5 (2021-11-07)

### New Feature

- Use new metadata utility for adding the ``image_field`` to the default serialization. This feature requires the JSONSummarySerializerMetadata serializer that has been added with plone.restapi 8.13.0.
  [@ericof]

### Internal:

- Use plone/setup-plone github action.
  [@ericof]


## 3.1.0a4 (2021-10-29)

### Internal:

- Initial support and tests using Github Actions for Plone with pip installations.
  [@ericof]

## 3.1.0a3 (2021-10-25)

### Breaking

- Explicitly require Python 3.7 or superior.
  [@ericof]

### Internal:

- Remove ``jq`` from dependencies and remove old ``blocksremoveserver.py`` script.
  [@ericof]

- Remove ``z3c.jbot`` from dependencies
  [@ericof]

- Remove ``requests`` from dependencies
  [@ericof]


## 3.1.0a2 (2021-10-14)

### Bug fix

- Fixed install on Windows, `issue 14 <https://github.com/plone/plone.volto/issues/14>`_.
  [@maurits]


## 3.1.0a1 (2021-10-11)

### Feature

- Add new ``image_field`` metadata for image detection in catalog
  [@sneridagh]

### Internal:

- Add Plone 6.0.0-pre-alpha configuration.
  [@tisto]

- Upgrade to Plone 5.2.5
  [@tisto]

- Change GS setup profile label to "Plone 6 Frontend (plone.volto)".
  [@tisto]


## 3.0.0a1 (2021-09-25)

### Breaking Change

- Rename kitconcept.volto to plone.volto.
  [@tisto]


## 2.5.3 (2021-09-13)

- Fix condition of the guard for the multilingual fixture in the docker image.
  [@sneridagh]


## 2.5.2 (2021-09-13)

- Fix multilingual fixture for docker image, the guard seems not to work there, for some reason the blocks and blocks_layout are not set yet (?)
  [@sneridagh]

## 2.5.1 (2021-09-12)

- "More agnostic and simplify GS profile for Plone Site definition" (https://github.com/kitconcept/kitconcept.volto/pull/38)
  [@sneridagh]

## 2.5.0 (2021-09-12)

- Support pip-based Plone installation by explicitly including dependencies on configure.zcml
  [@ericof]

- Add Lock-Token to default CORS allow_headers
  [@avoinea]

- Add guard for not overwrite blocks in default home pages (if PAM enabled) if they are already set
  [@sneridagh]

## 2.4.0 (2021-07-19)

- Fix German translation for "Navigation title" [@timo]

- Fix and complete upgrade step from Volto 12 to Volto 13
  [@sneridagh]

- Add helper scripts
  [@sneridagh]

- Add preview_image to transforms
  [@sneridagh]

- Add headtitle behavior
  [@sneridagh]

- Guard for setuphandlers disablecontenttype
  [@sneridagh]

- Fix audit script
  [@sneridagh]

- Add support for subblocks in the custom transforms for ``volto-blocks-grid``
  [@sneridagh]

## 2.3.0 (2021-05-19)

- Add upgrade step facility
- Add upgrade step from Volto 12 to Volto 13
  [@sneridagh]


## 2.2.1 (2021-04-21)

- Better multilingual profile
  [@sneridagh]


## 2.2.0 (2021-04-21)

- Add multilingual test fixture for Cypress tests
  [@sneridagh]


## 2.1.3 (2021-03-26)

- Add ``requests`` as dependency
  [@sneridagh]


## 2.1.2 (2021-03-07)

- Add a demo home page for demo site
  [@sneridagh]


## 2.1.1 (2021-03-06)

- Add demo site profile
  [@sneridagh]


## 2.1.0 (2021-02-23)

- Remove Images and Files from types_use_view_action_in_listings since in Volto it's no used at all.
  [@sneridagh]


## 2.0.0 (2021-02-20)

- [@Breaking] Define good known to work well with Volto image scales in ``registry.xml``
  GenericSetup profile. When this add-on is installed or the profile is applied, it will
  overwrite the existing scales in your Plone site. If you are using specific scales for
  your project, make sure they are installed after this addon's profile.

  This scales have been tested in real production projects and work well with Volto's
  layout and responsive viewports.
  [timo, sneridagh]


## 1.7.2 (2021-01-26)

- Nothing changed yet.


## 1.7.1 (2021-01-25)

- Fix first level tabs and add nav_title to them
  [@sneridagh]


## 1.7.0 (2021-01-21)

- Add ``breadcrumbs_view`` override to include ``nav_title``
  [@sneridagh]


## 1.6.0 (2021-01-14)

- Added indexers for `preview_image`, it allows the Volto object browser widget to access it
  [@sneridagh]


## 1.5.2 (2020-12-14)

- Missing ZCML for translations
  [@sneridagh]


## 1.5.1 (2020-12-14)

- Add zest.pocompile
  [@sneridagh]

- Add missing .mo
  [@sneridagh]


## 1.5.0 (2020-12-09)

- Fix locales default in German
  [@sneridagh]


## 1.4.0 (2020-07-29)

- Add volto.preview_image behavior to Page type.
  [@timo]


## 1.3.2 (2020-05-17)

- Make sure that the enable_pam helper does its job.
  [@sneridagh]


## 1.3.1 (2020-05-12)

- Fix LRF global allow and ensure default behaviors
  [@sneridagh]


## 1.3.0 (2020-05-11)

- Add registry navigation setting for not show the current item in navigations
  [@sneridagh]

- New enable_pam setuphandlers helper
  [@sneridagh]

- New enable_pam_consistency setuphandlers helper
  [@sneridagh]


## 1.2.0 (2020-04-17)

- Bring back the event type, since it's fully working in Volto now
  [@sneridagh]

- fix typo in behavior name ``navttitle`` -> ``navtitle``
  [@sneridagh]


## 1.1.0 (2020-03-10)

- Added a specific IImageScaleFactory for ``Image`` content type, to fix SVG handling
  [@sneridagh]


## 1.0.1 (2020-03-08)

- Update version numbers in default home page.
  [@sneridagh]


## 1.0.0 (2020-03-06)

- Add Zope log patch
  [@sneridagh]

- Add nav_title and preview_image behaviors
  [@sneridagh]

- override plone.app.vocabularies.Keywords with a version that
  uses the unencode subject value as the token.
  [@csenger]

- Remove versioning behavior from Document type.
  [@timo]

- Backport all features that were in plone.voltodemo
  [@sneridagh]

- Patch Password reset tool in Products.CMFPlone to use the optional volto_domain in the
  e-email which is sent to users, only if the request is made through REST.
  [@fredvd]

- Add Volto settings control panel with frontend_domain field.
  [@fredvd]

- Homepage profile for demo purposes
  [@sneridagh]

- CORS profile
  [@sneridagh]

- Enable Volto Blocks for Document and LRF
  [@sneridagh]

- Initial release.
  [@kitconcept]
