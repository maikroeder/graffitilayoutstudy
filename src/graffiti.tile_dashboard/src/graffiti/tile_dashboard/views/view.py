from typing import Dict, List

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from interaktiv.basetiles.views.basetile import BaseTileView
from zope.component import getMultiAdapter


class TileDashboardView(BaseTileView):
    """ Placeholder tile: renders dashboard boxes, the numbers are loaded by JavaScript.

    The boxes come from the adapter `IDashboardBoxesProvider`. Editors can only place and
    move the tile.
    """

    template = ViewPageTemplateFile('templates/view.pt')
    template_edit_mode = ViewPageTemplateFile('templates/view_edit_mode.pt')
    view_classes = ['tile-dashboard']
    # called by the tiles editor and for lazy loaded rows, see static/js/tile.js
    jsinit = 'initGraffitiTileDashboard'

    def get_boxes(self) -> List[Dict[str, str]]:
        provider = getMultiAdapter((self.context, self.request), IDashboardBoxesProvider)
        return provider.get_boxes()

    def is_tile_empty(self) -> bool:
        return not self.get_boxes()

    def data_url(self) -> str:
        return f'{self.context.absolute_url()}/@@tile_dashboard_data'
