import json
from typing import Dict, List, Optional

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_view import _, logger
from graffiti.tile_view.embed import EmbedError, get_view_entry, render_view
from interaktiv.basetiles.views.basetile import BaseTileView


class TileViewView(BaseTileView):
    """ Tile that embeds one of the registered views.

    Which views exist comes from the adapter `IEmbeddableViewsProvider`, editors pick one in
    the settings of the tile.
    """

    template = ViewPageTemplateFile('templates/view.pt')
    template_edit_mode = ViewPageTemplateFile('templates/view_edit_mode.pt')
    view_classes = ['tile-view']

    def get_entry(self) -> Optional[Dict[str, str]]:
        return get_view_entry(self.context, self.request, self.tile.get('view_id') or '')

    def is_tile_empty(self) -> bool:
        return self.get_entry() is None

    def get_html(self) -> str:
        """ The embedded view. Visitors get an empty tile if the view fails, editors an error. """
        view_id = self.tile.get('view_id') or ''
        try:
            return render_view(self.context, self.request, view_id)
        except EmbedError as e:
            logger.warning('view tile %s: %s', self.tile.get('id'), e)
            self.error = str(e)
            return ''

    def get_available_tile_actions(self) -> List[Dict]:
        actions = super().get_available_tile_actions()
        return self.append_tile_action(actions=actions, action={
            'action_id': 'configure_tileview_modal',
            'data_modal': '/configure_tileview_modal',
            'data_modal_size': 'md',
            'data_modal_request': json.dumps({'id': self.tile.get('id')}),
            'data_modal_params': json.dumps({
                'tagClass': 'configure_tileview_modal',
                'id': 'configure_tileview_modal',
            }),
            'data_modal_init': 'initializeConfigureTileViewModal',
            'attr_title': _('label_configure_view', default='Choose view'),
            'attr_class': 'tool interaktiv-icon-basetilestheme-tile-options',
            'visible': self.can_modify(),
        }, position=0)
