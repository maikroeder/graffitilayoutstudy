from graffiti.pdfcheck.messages import _
from graffiti.pdfcheck.registry.pdfcheck import IPdfCheckSettings
from graffiti.pdfcheck.widgets.checks import ChecksFieldWidget
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper, RegistryEditForm
from plone.autoform import directives
from plone.z3cform import layout
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.schema import getFieldNamesInOrder
from zope.schema.interfaces import ValidationError


class NoCheckChosen(ValidationError):
    __doc__ = _('error_no_check', default='Choose at least one check. To switch the check off, untick '
                                          '"Check PDF files on upload".')


def at_least_one_check(value):
    """ An empty list would mean all built-in checks, not "no check" """
    if not value:
        raise NoCheckChosen(value)
    return True


class IPdfCheckSettingsForm(IPdfCheckSettings):
    """ The settings page offers only content types with a file field named "file", and the available checks """

    directives.widget('portal_types', CheckBoxFieldWidget)
    portal_types = schema.List(
        title=_('label_portal_types', default='Content types'),
        description=_('help_portal_types', default='PDF files of these content types are checked. Only content '
                                                   'types with a file field are offered.'),
        value_type=schema.Choice(vocabulary='graffiti.pdfcheck.FileTypes'),
        required=False,
    )

    # with the name and the function of each check, for developers
    directives.widget('checks', ChecksFieldWidget)
    checks = schema.List(
        title=_('label_checks', default='Checks'),
        description=_('help_checks', default='These checks run for every PDF file.'),
        value_type=schema.Choice(vocabulary='graffiti.pdfcheck.Checks'),
        constraint=at_least_one_check,
        required=False,
    )


class PdfCheckSettingsForm(RegistryEditForm):
    schema = IPdfCheckSettingsForm
    schema_prefix = 'graffiti.pdfcheck'
    label = _('label_settings', default='PDF check settings')
    description = _('help_settings', default='Checks PDF files on upload whether they can be processed later.')

    def updateFields(self):
        super(PdfCheckSettingsForm, self).updateFields()
        # the form schema redefines a field, keep the order of the settings
        self.fields = self.fields.select(*getFieldNamesInOrder(IPdfCheckSettings))


PdfCheckSettingsView = layout.wrap_form(PdfCheckSettingsForm, ControlPanelFormWrapper)
