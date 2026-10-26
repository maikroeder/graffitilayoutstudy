from typing import Dict, List

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_tabs.interfaces import ITabListsProvider
from interaktiv.basetiles.views.basetile import BaseTileView
from zope.component import getMultiAdapter


class TileTabsView(BaseTileView):
    """ Placeholder tile: renders lists in tabs, server side.

    The tabs come from the adapter `ITabListsProvider`. Editors can only place and move the
    tile. Switching tabs is done by `static/js/tile.js`, a delegated handler that needs no
    initialisation per tile.
    """

    template = ViewPageTemplateFile('templates/view.pt')
    template_edit_mode = ViewPageTemplateFile('templates/view_edit_mode.pt')
    view_classes = ['tile-tabs']

    def get_tabs(self) -> List[Dict]:
        provider = getMultiAdapter((self.context, self.request), ITabListsProvider)
        return provider.get_tabs()

    def is_tile_empty(self) -> bool:
        return not self.get_tabs()
