# -*- coding: utf-8 -*-
"""Installer for the plone.volto package."""

from setuptools import find_packages
from setuptools import setup


def readfile(name):
    with open(name, encoding="utf-8") as myfile:
        return myfile.read()


long_description = "\n\n".join(
    [
        readfile("README.rst"),
        readfile("CONTRIBUTORS.rst"),
        readfile("CHANGES.rst"),
    ]
)

setup(
    name="plone.volto",
    version="3.1.0a2.dev0",
    description="Volto integration add-on for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="kitconcept GmbH",
    author_email="info@kitconcept.com",
    url="https://github.com/plone/plone.volto",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "plone.api",
        "Products.GenericSetup>=1.8.2",
        "setuptools",
        "z3c.jbot",
        "plone.restapi",
        "collective.folderishtypes[dexterity]",
        "requests",
        "jq",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
