import json

from Products.Five.browser import BrowserView
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from zope.component import getMultiAdapter


class TileDashboardDataView(BrowserView):
    """ JSON with the numbers of the dashboard boxes for the current user """

    def __call__(self) -> str:
        provider = getMultiAdapter((self.context, self.request), IDashboardBoxesProvider)
        response = self.request.response
        response.setHeader('Content-Type', 'application/json')
        # the numbers depend on the user and change with the content
        response.setHeader('Cache-Control', 'private, no-store')
        return json.dumps({'counts': provider.get_counts()})
