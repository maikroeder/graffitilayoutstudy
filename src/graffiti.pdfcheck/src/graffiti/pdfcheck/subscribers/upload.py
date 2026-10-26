""" Checks PDF files when they are added or changed. The upload is never rejected. """
import logging

from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from graffiti.pdfcheck.api import check_object
from graffiti.pdfcheck.messages import _, finding_label, hint_texts
from graffiti.pdfcheck.settings import FIELD
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest
from zope.i18n import translate

logger = logging.getLogger('graffiti.pdfcheck')


def on_added(obj, event):
    check_and_tell(obj)


def on_modified(obj, event):
    if IContainerModifiedEvent.providedBy(event) or not file_may_have_changed(event):
        return
    check_and_tell(obj)


def file_may_have_changed(event):
    """ Edit forms and the REST API name the changed fields. Without names the checksum decides. """
    names = [name for description in getattr(event, 'descriptions', ()) or ()
             for name in getattr(description, 'attributes', ())]
    if not names:
        return True
    return any(name == FIELD or name.endswith('.' + FIELD) for name in names)


def check_and_tell(obj):
    try:
        result = check_object(obj)
    except ConflictError:
        # Zope repeats the request
        raise
    except Exception:  # noqa: the check must never stop an upload
        logger.exception('PDF check of %s failed', '/'.join(obj.getPhysicalPath()))
        return
    if result is not None:
        show_message(result)


def show_message(result, request=None):
    """ A status message for the editor after the upload, only for findings and hints """
    request = request if request is not None else getRequest()
    if request is None or not (result.get('findings') or result.get('hints')):
        return
    if is_api_request(request):
        return
    # the texts are whole sentences
    if result.get('findings'):
        reasons = ' '.join(finding_label(code, request) for code in result['findings'])
        message = _('message_findings', default='PDF check: the file was saved, but it can probably not be processed '
                                                'later. ${reasons}', mapping={'reasons': reasons})
        message_type = 'warning'
    else:
        hints = ' '.join(hint_texts(result['hints'], request))
        message = _('message_hints', default='PDF check: the file was saved. Please note: ${hints}',
                    mapping={'hints': hints})
        message_type = 'info'
    IStatusMessage(request).add(translate(message, context=request), type=message_type)


def is_api_request(request):
    """ The REST API answers with JSON, a status message would only show up on the next page """
    try:
        from plone.rest.interfaces import IAPIRequest
    except ImportError:
        return False
    return IAPIRequest.providedBy(request)
