from setuptools import find_packages
from setuptools import setup


# We must specify the encoding, otherwise it fails on Windows as it defaults to cp1252.
long_description = "\n\n".join(
    [
        open("README.md", encoding="utf-8").read(),
        open("CHANGES.md", encoding="utf-8").read(),
    ]
)


setup(
    name="plone.volto",
    version="5.1.0",
    description="Volto integration add-on for Plone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="Plone Foundation",
    author_email="tisto@plone.org",
    url="https://github.com/plone/plone.volto",
    license="GPL version 2",
    packages=find_packages("src"),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "collective.monkeypatcher",
        "plone.api",
        "plone.app.caching",
        "plone.app.dexterity",
        "plone.distribution",
        "plone.restapi>=8.41.0",
        "Products.CMFPlone",
        "setuptools",
    ],
    extras_require={
        "test": [
            "responses",
            "plone.app.discussion",
            "plone.app.iterate",
            "plone.app.multilingual",
            "plone.app.robotframework",
            "plone.app.testing",
            "plone.app.upgrade",
            "plone.restapi[test]",
            "plone.testing",
            "Products.CMFPlacefulWorkflow",
            "pytest-plone>=0.5.0",
        ]
    },
    entry_points="""
    [console_scripts]
    update_locale = plone.volto.locales.update:update_locale
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
