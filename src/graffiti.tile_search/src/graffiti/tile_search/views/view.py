from typing import Dict, Optional

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_search.interfaces import ISearchTileSettings
from interaktiv.basetiles.views.basetile import BaseTileView
from zope.component import getMultiAdapter


class TileSearchView(BaseTileView):
    """ Placeholder tile: renders a search form with live results.

    Reuses the pattern `pat-livesearch` of Plone. Where the search goes comes from the adapter
    `ISearchTileSettings`. Editors can only place and move the tile.
    """

    template = ViewPageTemplateFile('templates/view.pt')
    template_edit_mode = ViewPageTemplateFile('templates/view_edit_mode.pt')
    view_classes = ['tile-search']

    def get_settings(self) -> ISearchTileSettings:
        return getMultiAdapter((self.context, self.request), ISearchTileSettings)

    def search_url(self) -> str:
        return self.get_settings().get_search_url()

    def form_classes(self) -> str:
        classes = 'tile-search-form'
        if self.get_settings().get_livesearch_url():
            classes += ' pat-livesearch'
        return classes

    def livesearch_options(self) -> Optional[str]:
        livesearch_url = self.get_settings().get_livesearch_url()
        return f'ajaxUrl:{livesearch_url}' if livesearch_url else None

    def parameters(self) -> Dict[str, str]:
        return self.get_settings().get_parameters()

    def search_parameter_name(self) -> str:
        return self.get_settings().get_search_parameter_name() or 'SearchableText'

    def input_id(self) -> str:
        # a tile can be placed several times on one page, so the id has to be unique per tile
        return f'tile-search-{self.tile.get("id")}'
