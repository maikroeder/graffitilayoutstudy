from typing import Dict, Optional

from graffiti.tile_search.interfaces import ISearchTileSettings
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from plone import api
from zope.component import adapter
from zope.interface import Interface, implementer


@implementer(ISearchTileSettings)
@adapter(ITilePage, Interface)
class SiteSearchSettings:
    """ Default: the search of Plone for the whole navigation root, with live results. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def navigation_root_url(self) -> str:
        return api.portal.get_navigation_root(context=self.context).absolute_url()

    def get_search_url(self) -> str:
        return f'{self.navigation_root_url()}/@@search'

    def get_livesearch_url(self) -> Optional[str]:
        return f'{self.navigation_root_url()}/@@ajax-search'

    def get_parameters(self) -> Dict[str, str]:
        return {}

    def get_search_parameter_name(self) -> str:
        return 'SearchableText'
