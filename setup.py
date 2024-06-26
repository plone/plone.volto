from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.md").read(),
        open("CHANGES.md").read(),
    ]
)


setup(
    name="plone.volto",
    version="5.0.0a1.dev0",
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
        "plone.api",
        "Products.GenericSetup",
        "setuptools",
        "plone.restapi>=8.41.0",
        "plone.app.vocabularies>=4.3.0",
        "plone.distribution",
        "Products.CMFPlacefulWorkflow",
        "plone.app.caching",
        "plone.app.discussion",
        "plone.app.iterate",
        "plone.app.multilingual",
        "Products.CMFPlone",
        "collective.monkeypatcher",
    ],
    extras_require={
        "test": [
            "responses",
            "plone.app.testing",
            "plone.app.upgrade",
            "plone.testing",
            "pytest-cov",
            "pytest-plone>=0.5.0",
            "zest.releaser[recommended]",
            "zestreleaser.towncrier",
        ]
    },
    entry_points="""
    [console_scripts]
    update_locale = plone.volto.locales.update:update_locale
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
