from typing import Dict, List

from graffiti.tile_view import _
from graffiti.tile_view.interfaces import IEmbeddableViewsProvider, MODE_AJAX_LOAD, MODE_VIEW
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from plone import api
from zope.component import adapter
from zope.i18n import translate
from zope.interface import Interface, implementer


@implementer(IEmbeddableViewsProvider)
@adapter(ITilePage, Interface)
class DefaultViewsProvider:
    """ Default: three examples.

    * the example view of this package (mode `view`, renders a fragment)
    * the search page of Plone (mode `ajax_load`, a normal page cut down to its content area)
    * the sitemap of Plone (mode `ajax_load`, plain HTML without JavaScript)
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def navigation_root_url(self) -> str:
        return api.portal.get_navigation_root(context=self.context).absolute_url()

    def get_views(self) -> List[Dict[str, str]]:
        root = self.navigation_root_url()
        return [
            {
                'id': 'example-recent',
                'title': translate(_('label_view_example_recent', default='Example: recently changed'), context=self.request),
                'description': translate(_(
                    'help_view_example_recent',
                    default='The ten most recently changed items the current user may see. Frameless view of this package.'
                ), context=self.request),
                'url': f'{root}/@@tile-view-example-recent',
                'mode': MODE_VIEW,
            },
            {
                'id': 'plone-search',
                'title': translate(_('label_view_plone_search', default='Search page of Plone'), context=self.request),
                'description': translate(_(
                    'help_view_plone_search',
                    default='The normal search page, cut down to its content area via ajax_load.'
                ), context=self.request),
                'url': f'{root}/@@search',
                'mode': MODE_AJAX_LOAD,
            },
            {
                'id': 'plone-sitemap',
                'title': translate(_('label_view_plone_sitemap', default='Sitemap of Plone'), context=self.request),
                'description': translate(_(
                    'help_view_plone_sitemap',
                    default='The sitemap page, cut down to its content area via ajax_load. Plain HTML without JavaScript.'
                ), context=self.request),
                'url': f'{root}/@@sitemap',
                'mode': MODE_AJAX_LOAD,
            },
        ]
