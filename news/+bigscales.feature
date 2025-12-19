Add larger scales to `plone.allowed_sizes` for new sites. This helps avoid the
need to serve the original image which can be very large. @davisagli

- `2k` is large enough for a default-width image on a high-density display.
- `4k` is large enough for a full-width images on high-density viewports up to 2000 pixels wide.
