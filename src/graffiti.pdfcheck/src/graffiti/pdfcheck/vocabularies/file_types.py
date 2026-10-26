import logging

from Products.CMFCore.utils import getToolByName
from graffiti.pdfcheck.settings import FIELD
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import iterSchemataForType
from plone.namedfile.interfaces import INamedFileField
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

logger = logging.getLogger('graffiti.pdfcheck')


def has_file_field(portal_type):
    """ A file field with the name the check reads, in the schema of the type or in one of its behaviors """
    try:
        schemata = list(iterSchemataForType(portal_type))
    except Exception:  # noqa: RecursionError and others, a type must not break the settings page
        # for example a type of a removed package: its schema can not be imported, and without a model
        # plone.dexterity looks for it again and again
        logger.warning('The schema of the content type %s can not be loaded, it is not offered', portal_type)
        return False
    for schema in schemata:
        field = schema.get(FIELD)
        if field is not None and INamedFileField.providedBy(field):
            return True
    return False


@provider(IVocabularyFactory)
def FileTypesVocabularyFactory(context):
    types_tool = getToolByName(getSite(), 'portal_types', None)
    if types_tool is None:
        return SimpleVocabulary([])
    request = getRequest()
    terms = [SimpleTerm(fti.getId(), fti.getId(), translate(fti.Title(), context=request))
             for fti in types_tool.listTypeInfo() if IDexterityFTI.providedBy(fti) and has_file_field(fti.getId())]
    return SimpleVocabulary(sorted(terms, key=lambda term: term.title.lower()))
