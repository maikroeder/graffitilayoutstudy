from graffiti.pdfcheck.messages import CHECK_LABELS
from graffiti.pdfcheck.settings import available_checks
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


@provider(IVocabularyFactory)
def ChecksVocabularyFactory(context):
    """ The built-in checks and the registered checks of projects, in the order they run """
    request = getRequest()
    return SimpleVocabulary([
        SimpleTerm(check.name, check.name, translate(CHECK_LABELS.get(check.name, check.title or check.name),
                                                     context=request))
        for check in available_checks()])
