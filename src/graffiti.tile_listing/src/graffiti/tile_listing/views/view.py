from typing import Dict, List

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_listing.interfaces import IListingItemsProvider
from interaktiv.basetiles.views.basetile import BaseTileView
from zope.component import getMultiAdapter


class TileListingView(BaseTileView):
    """ Placeholder tile: renders a listing.

    The entries come from the adapter `IListingItemsProvider`. Editors can only place and
    move the tile.
    """

    template = ViewPageTemplateFile('templates/view.pt')
    template_edit_mode = ViewPageTemplateFile('templates/view_edit_mode.pt')
    view_classes = ['tile-listing']

    def get_provider(self) -> IListingItemsProvider:
        return getMultiAdapter((self.context, self.request), IListingItemsProvider)

    def get_label(self) -> str:
        return self.get_provider().get_label()

    def get_items(self) -> List[Dict[str, str]]:
        return self.get_provider().get_items()
