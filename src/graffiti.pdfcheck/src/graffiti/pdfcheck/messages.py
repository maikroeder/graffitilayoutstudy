""" Texts for editors, translated with the domain graffiti.pdfcheck """
from graffiti.pdfcheck.checks import FINDINGS, HINTS
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('graffiti.pdfcheck')

FINDING_LABELS = {
    'damaged': _('finding_damaged', default='The file is damaged and can not be opened.'),
    'crypto_missing': _('finding_crypto_missing', default='The file is encrypted and could not be checked completely.'),
    'password': _('finding_password', default='The file is protected with a password.'),
    'edit_protection': _('finding_edit_protection', default='The file has an edit protection.'),
    'no_text': _('finding_no_text', default='No text can be read from the file, for example because it is a scan.'),
    'rewrite': _('finding_rewrite', default='The pages of the file can not be put together again.'),
    'pdfunite': _('finding_pdfunite', default='No second PDF file can be appended to the file.'),
    'qpdf': _('finding_qpdf', default='The inner structure of the file has errors.'),
    'timeout': _('finding_timeout', default='The check took too long and was stopped.'),
    'memory': _('finding_memory', default='The check needed too much memory and was stopped.'),
    'check_error': _('finding_check_error', default='The check could not run.'),
}

HINT_LABELS = {
    'qpdf_warnings': _('hint_qpdf_warnings',
                       default='The inner structure has small errors that can be repaired automatically.'),
    'not_checked': _('hint_not_checked', default='The file was not checked.'),
}

# what a later processing loses, named together in one sentence
LOST_LABELS = {
    'lost_outlines': _('lost_outlines', default='bookmarks'),
    'lost_form_fields': _('lost_form_fields', default='form fields'),
    'lost_signatures': _('lost_signatures', default='signatures'),
    'lost_embedded_files': _('lost_embedded_files', default='embedded files'),
}

# the built-in checks on the settings page
CHECK_LABELS = {
    'open': _('check_open', default='Open the file: damaged, password, edit protection'),
    'text': _('check_text', default='Read the text: files without text, for example scans'),
    'rewrite': _('check_rewrite', default='Put the pages together again and add metadata'),
    'pdfunite': _('check_pdfunite', default='Append a second PDF file (program pdfunite)'),
    'qpdf': _('check_qpdf', default='Check the inner structure (program qpdf)'),
}

STEP_LABELS = {
    'header': _('step_header', default='PDF header'),
    'size': _('step_size', default='File size'),
    'open': _('step_open', default='Open'),
    'text': _('step_text', default='Read the text'),
    'rewrite': _('step_rewrite', default='Rebuild page by page'),
    'pdfunite': _('step_pdfunite', default='Append a second PDF'),
    'qpdf': _('step_qpdf', default='Check the structure'),
    'runner': _('step_runner', default='Check process'),
}


def project_labels():
    """ The titles and the texts of the registered checks of projects """
    # imported here: the settings import this module through the interfaces
    from graffiti.pdfcheck.settings import available_checks
    titles, texts = {}, {}
    for check in available_checks():
        if check.title:
            titles[check.name] = check.title
        texts.update(check.texts or {})
    return titles, texts


def finding_label(code, request):
    """ A code without a text, for example of a check of a project without texts, shows its English text or the code """
    label = FINDING_LABELS.get(code) or project_labels()[1].get(code) or FINDINGS.get(code, code)
    return translate(label, context=request)


def hint_label(code, request):
    label = HINT_LABELS.get(code) or project_labels()[1].get(code) or HINTS.get(code, code)
    return translate(label, context=request)


def hint_texts(codes, request):
    """ One sentence per hint, the parts that get lost together in one sentence """
    lost = [translate(LOST_LABELS[code], context=request) for code in codes if code in LOST_LABELS]
    texts = []
    for code in codes:
        if code not in LOST_LABELS:
            texts.append(hint_label(code, request))
        elif lost:
            texts.append(translate(_('hint_lost', default='When the file is processed, these are lost: ${items}.',
                                     mapping={'items': ', '.join(lost)}), context=request))
            lost = []
    return texts


def step_label(name, request):
    return translate(STEP_LABELS.get(name) or project_labels()[0].get(name, name), context=request)
