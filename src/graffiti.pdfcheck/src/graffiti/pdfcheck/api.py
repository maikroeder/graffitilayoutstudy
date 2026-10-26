""" The result of the check at the object, for projects and for conditions in workflows.

    from graffiti.pdfcheck import api
    api.is_suitable(obj)   # True, False or None (no PDF, not checked, or checked before the installation)
    api.check_object(obj)  # checks the file of the object and stores the result
"""
import hashlib
import logging
import os
import tempfile
from contextlib import contextmanager
from copy import deepcopy

from Acquisition import aq_base
from ZODB.POSException import ConflictError
from graffiti.pdfcheck.checks import add_step, finish, new_result, ok, skipped
from graffiti.pdfcheck.interfaces import IPdfCheckRunner
from graffiti.pdfcheck.runner import too_large
from graffiti.pdfcheck.settings import FIELD, get_settings
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility

logger = logging.getLogger('graffiti.pdfcheck')

ANNOTATION_KEY = 'graffiti.pdfcheck'
CHUNK = 1024 * 1024
# results that say more about the check than about the file: the file is checked again, even if it is the same
INCOMPLETE_FINDINGS = {'timeout', 'memory', 'check_error', 'crypto_missing'}


def get_result(obj):
    """ A copy of the stored result, None if the file of the object was not checked """
    result = IAnnotations(obj, {}).get(ANNOTATION_KEY)
    return deepcopy(result) if result is not None else None


def set_result(obj, result):
    IAnnotations(obj)[ANNOTATION_KEY] = deepcopy(result)


def delete_result(obj):
    annotations = IAnnotations(obj, None)
    if annotations is not None and ANNOTATION_KEY in annotations:
        del annotations[ANNOTATION_KEY]


def is_suitable(obj):
    """ True: no findings. False: at least one finding. None: no result or not checked. """
    result = get_result(obj)
    return result.get('suitable') if result else None


def get_findings(obj):
    result = get_result(obj)
    return list(result.get('findings') or []) if result else []


def get_hints(obj):
    result = get_result(obj)
    return list(result.get('hints') or []) if result else []


def check_object(obj, force=False, settings=None):
    """ Checks the PDF file of the object and stores the result at the object.

    Returns the new result, None if nothing was checked: the check is switched off, the content type is not
    in the settings, the object has no PDF file, or the file did not change since the last check (`force` checks it
    again anyway). Without a check a stored result is removed, it could belong to an older file.
    """
    settings = settings or get_settings()
    if not settings or not settings['enabled'] or getattr(obj, 'portal_type', None) not in settings['portal_types']:
        delete_result(obj)
        return None
    named_file = getattr(aq_base(obj), FIELD, None)
    if named_file is None or not named_file.getSize():
        delete_result(obj)
        return None
    with _file_path(named_file) as path:
        with open(path, 'rb') as pdf_file:
            if b'%PDF-' not in pdf_file.read(1024):
                # files that are no PDF stay untouched
                delete_result(obj)
                return None
            size = named_file.getSize()
            if settings['max_size_mb'] and size > settings['max_size_mb'] * 1024 * 1024:
                # no need to read a file that is not checked anyway
                result = too_large(size, settings['max_size_mb'])
                checksum = None
            else:
                result = None
                checksum = _sha256(pdf_file)
        stored = get_result(obj)
        if not force and result is None and stored and stored.get('sha256') == checksum and is_complete(stored):
            return None
        try:
            result = result or getUtility(IPdfCheckRunner).check(path, settings)
        except ConflictError:
            # a runner of a project may read from the database
            raise
        except Exception as error:  # noqa: a broken setting or service must not stop the upload
            logger.exception('PDF check of %s could not run', '/'.join(obj.getPhysicalPath()))
            result = _not_checked(error)
        _rename_in_texts(result, os.path.basename(path), getattr(named_file, 'filename', None))
    result.update({
        'sha256': checksum,
        'size': named_file.getSize(),
        'filename': getattr(named_file, 'filename', None),
        'field': FIELD,
    })
    set_result(obj, result)
    return result


def is_complete(result):
    """ False if a check could not run, for example because of the time limit """
    return not (set(result.get('findings') or []) & INCOMPLETE_FINDINGS or 'not_checked' in (result.get('hints') or []))


def _rename_in_texts(result, name, filename):
    """ Messages of programs name the blob file, editors know the file by its filename """
    if not filename or not name:
        return
    for step in result.get('steps', {}).values():
        if step.get('text'):
            step['text'] = step['text'].replace(name, filename)


def _sha256(open_file):
    open_file.seek(0)
    digest = hashlib.sha256()
    for chunk in iter(lambda: open_file.read(CHUNK), b''):
        digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def _file_path(named_file):
    """ The path of the file on the disk: the blob file itself, or a temporary copy of a file without blob """
    blob = getattr(named_file, '_blob', None)
    if blob is not None:
        with blob.open('r') as blob_file:
            yield blob_file.name
    else:
        with tempfile.NamedTemporaryFile(prefix='pdfcheck-', suffix='.pdf') as temporary:
            temporary.write(named_file.data)
            temporary.flush()
            yield temporary.name


def _not_checked(error):
    result = new_result()
    result['is_pdf'] = True
    add_step(result, 'header', 'script', ok('found'))
    add_step(result, 'runner', 'runner', skipped('not checked: %s' % error, ['not_checked']))
    return finish(result)
