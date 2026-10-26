from graffiti.pdfcheck.checks import function_name
from graffiti.pdfcheck.settings import available_checks
from graffiti.pdfcheck.widgets.interfaces import IChecksWidget
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component.hooks import getSite
from zope.interface import implementer, implementer_only


@implementer_only(IChecksWidget)
class ChecksWidget(CheckBoxWidget):
    """ The checks as a table with their name and their function, for developers, like the behaviors of a type """

    def css_url(self):
        return getSite().absolute_url() + '/++resource++graffiti.pdfcheck/pdfcheck.css'

    def rows(self):
        checks = {check.name: check for check in available_checks()}
        rows = []
        for item in self.items:
            check = checks.get(item['value'])
            rows.append(dict(item, check_name=item['value'], function=function_name(check) if check else ''))
        return rows


@implementer(IFieldWidget)
def ChecksFieldWidget(field, request):
    return FieldWidget(field, ChecksWidget(request))
