#!/bin/bash

set -euxo pipefail

domain=plone.volto
maindir=src/plone/volto
locales=$maindir/locales
echo "Update translations for $domain"
if [ ! -f $locales/$domain.pot ]; then
    # Create .pot file if it does not exist yet
    touch $locales/$domain.pot
fi
if [ ! -f $locales/de/LC_MESSAGES ]; then
    # Create de/LC_MESSAGES directory if it does not exist yet
    mkdir -p $locales/de/LC_MESSAGES
fi
if [ ! -f $locales/de/LC_MESSAGES/$domain.po ]; then
    # Create .po file if it does not exist yet
    touch $locales/de/LC_MESSAGES/$domain.po
fi
bin/i18ndude rebuild-pot --pot $locales/$domain.pot --create $domain $maindir
bin/i18ndude sync --pot $locales/$domain.pot $locales/*/LC_MESSAGES/$domain.po
