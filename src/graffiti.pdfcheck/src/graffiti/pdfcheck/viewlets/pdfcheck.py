from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.pdfcheck import api
from graffiti.pdfcheck.checks import FINDINGS
from graffiti.pdfcheck.messages import finding_label, hint_texts, step_label
from graffiti.pdfcheck.settings import get_settings
from plone.app.layout.viewlets.common import ViewletBase
import plone.api

try:
    import plone.base  # noqa: F401
    # Plone 6: the classes of its status messages
    WARNING_CLASSES = 'portalMessage statusmessage statusmessage-warning alert alert-warning'
    INFO_CLASSES = 'portalMessage statusmessage statusmessage-info alert alert-info'
except ImportError:
    # Plone 5.2: the Bootstrap 3 class "alert" would change the padding of the message
    WARNING_CLASSES = 'portalMessage warning'
    INFO_CLASSES = 'portalMessage info'


class PdfCheckViewlet(ViewletBase):
    """ The result of the check in the view of the file, for users who may change the file """

    index = ViewPageTemplateFile('templates/pdfcheck.pt')
    result = None

    def update(self):
        super(PdfCheckViewlet, self).update()
        settings = get_settings()
        if not settings or not settings['enabled']:
            return
        result = api.get_result(self.context)
        if result and (result.get('findings') or result.get('hints')):
            self.result = result

    def render(self):
        return self.index() if self.result else ''

    def box_classes(self):
        """ A warning with findings, otherwise only a note """
        return 'graffiti-pdfcheck ' + (WARNING_CLASSES if self.result.get('findings') else INFO_CLASSES)

    def css_url(self):
        return self.site_url + '/++resource++graffiti.pdfcheck/pdfcheck.css'

    def findings(self):
        return [finding_label(code, self.request) for code in self.result.get('findings', [])]

    def hints(self):
        return hint_texts(self.result.get('hints', []), self.request)

    def details(self):
        """ What the steps with findings or hints say, in the words of the programs """
        items = []
        for name, step in self.result['steps'].items():
            text = step.get('text') or ''
            if not text or not (step.get('finding') or step.get('hints')):
                continue
            # the text only when it says more than the finding itself
            known = FINDINGS.get(step.get('finding'))
            if known and text.startswith(known):
                continue
            items.append({'step': step_label(name, self.request), 'text': text})
        return items

    def checked_at(self):
        try:
            return plone.api.portal.get_localized_time(DateTime(self.result['checked_at']), long_format=True)
        except Exception:  # noqa: an unreadable date is no reason to hide the result
            return self.result.get('checked_at', '')

    def tools(self):
        versions = self.result.get('versions') or {}
        return ', '.join('%s %s' % (name, versions[name]) for name in ('pypdf', 'pdfunite', 'qpdf')
                         if versions.get(name))
