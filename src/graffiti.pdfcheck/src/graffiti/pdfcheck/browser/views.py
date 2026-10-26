import json

from Products.Five.browser import BrowserView
from graffiti.pdfcheck import api


class PdfCheckView(BrowserView):
    """ The result for conditions in workflows:

        python: here.restrictedTraverse('@@pdfcheck').suitable() is not False
    """

    def suitable(self):
        return api.is_suitable(self.context)

    def findings(self):
        return api.get_findings(self.context)

    def hints(self):
        return api.get_hints(self.context)

    def has_finding(self, code):
        return code in self.findings()

    def __call__(self):
        result = api.get_result(self.context) or {}
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps({
            'suitable': result.get('suitable'),
            'findings': result.get('findings', []),
            'hints': result.get('hints', []),
            'checked_at': result.get('checked_at'),
        })
