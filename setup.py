# -*- coding: utf-8 -*-
"""Installer for the plone.volto package."""

from setuptools import find_packages
from setuptools import setup

import sys


assert sys.version_info >= (3, 6, 0), "plone.volto requires Python 3.7.0."


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
    version="4.0.7",
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Plone Foundation",
    author_email="tisto@plone.org",
    url="https://github.com/plone/plone.volto",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "plone.api",
        "Products.GenericSetup",
        "setuptools",
        "plone.restapi>=8.13.0",
        "plone.app.vocabularies>=4.3.0",
        "collective.monkeypatcher",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            "plone.testing",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            "collective.MockMailHost",
            "responses",
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
