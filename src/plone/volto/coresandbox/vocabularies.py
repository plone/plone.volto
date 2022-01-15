from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


@provider(IVocabularyFactory)
def DocumentVocabularyFactory(context=None):
    return StaticCatalogVocabulary(
        {
            "portal_type": ["Document", "News Item"],
            "sort_on": "sortable_title",
        }
    )


@provider(IVocabularyFactory)
def HugeVocabularyFactory(context=None):
    terms = []
    for a in range(1000):
        terms.append(
            SimpleVocabulary.createTerm(f"option{a}", f"option{a}", f"Option {a}")
        )

    return SimpleVocabulary(sorted(terms, key=lambda term: term.title))
