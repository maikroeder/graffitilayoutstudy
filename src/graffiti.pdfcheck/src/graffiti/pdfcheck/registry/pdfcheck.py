from graffiti.pdfcheck.messages import _
from plone.supermodel import model
from zope import schema

DEFAULT_CHECKS = ['open', 'text', 'rewrite', 'pdfunite', 'qpdf']


class IPdfCheckSettings(model.Schema):
    """ The settings of the PDF check, records in the registry with the prefix `graffiti.pdfcheck` """

    enabled = schema.Bool(
        title=_('label_enabled', default='Check PDF files on upload'),
        description=_('help_enabled', default='The upload is never rejected. Editors get a message about the result.'),
        default=True,
        required=False,
    )

    # plain names in the registry: a type that was removed or lost its file field must not break anything
    portal_types = schema.List(
        title=_('label_portal_types', default='Content types'),
        description=_('help_portal_types', default='PDF files of these content types are checked. Only content '
                                                   'types with a file field are offered.'),
        value_type=schema.TextLine(),
        default=['File'],
        required=False,
    )

    # the names of the checks that run: built-in checks (graffiti.pdfcheck.checks.BUILTIN_CHECKS) and registered
    # checks of projects (IPdfCheck); plain names, so that a check of a removed package breaks nothing
    checks = schema.List(
        title=_('label_checks', default='Checks'),
        description=_('help_checks', default='These checks run for every PDF file.'),
        value_type=schema.TextLine(),
        default=list(DEFAULT_CHECKS),
        required=False,
    )

    timeout = schema.Int(
        title=_('label_timeout', default='Time limit in seconds'),
        description=_('help_timeout', default='How long the check of one file may take. The editor waits for it '
                                               'when uploading.'),
        default=30,
        min=1,
    )

    memory_mb = schema.Int(
        title=_('label_memory_mb', default='Memory limit in MB'),
        description=_('help_memory_mb', default='How much memory the check of one file may use. It runs in a process '
                                                 'of its own.'),
        default=1024,
        min=64,
    )

    max_size_mb = schema.Int(
        title=_('label_max_size_mb', default='Largest file in MB'),
        description=_('help_max_size_mb', default='Larger files are not checked, the editor gets a hint.'),
        default=50,
        min=1,
    )
