import json
from typing import Dict
from typing import List
from typing import Optional

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interaktiv.basetiles.views.basetile import BaseTileView
from interaktiv.framework import vocabulary as framework_vocabulary
from openheidelberg.tile_card import _
from openheidelberg.tile_card.vocabularies.orientation import DEFAULT_ICON_ORIENTATION
from openheidelberg.tile_card.vocabularies.svg_icons import read_svg_icon


class TileCardView(BaseTileView):
    """Card: image, title, short description and a single primary action."""

    template = ViewPageTemplateFile('templates/view.pt')
    view_classes = ['tile-card']

    def get_image(self) -> Optional[Dict[str, str]]:
        ref = self.tile.get('image', None)
        if not ref or ref.isBroken():
            return None
        obj = ref.to_object
        if obj is None:
            return None
        return {
            'url': obj.absolute_url() + '/@@images/image/large',
            'alt': self.tile.get('image_alt', '') or '',
        }

    def get_link(self) -> Optional[Dict[str, str]]:
        href = (self.tile.get('link_href', '') or '').strip()
        if not href:
            return None
        if href.startswith('/'):
            href = self.context.portal_url() + href
        label = (self.tile.get('link_label', '') or '').strip()
        if not label:
            label = self.context.translate(_('label_card_default_action', default='Read more'))
        new_window = bool(self.tile.get('link_new_window', False))
        show_button = self.tile.get('link_show_button', None)
        if show_button is None:
            show_button = True  # cards created before the option existed keep their button
        return {
            'href': href,
            'label': label,
            'show_button': bool(show_button),
            'target': '_blank' if new_window else '',
            'rel': 'noopener' if new_window else '',
        }

    def get_icon(self) -> str:
        """CSS class of the chosen icon; empty if none is set or the value is not a known icon."""
        value = self.tile.get('card_icon', '') or ''
        if not value:
            return ''
        vocab = framework_vocabulary.get_vocabulary(ident='TileCard', field='card_icon')
        if value in vocab.by_value:
            return vocab.getTerm(value).value
        if value in vocab.by_token:
            return vocab.getTermByToken(value).value
        return ''

    def get_svg_icon(self) -> str:
        """Markup of the chosen svg icon; empty if none is set or the name is not in the icon registry."""
        return read_svg_icon(self.tile.get('card_icon_svg', '') or '')

    def get_icon_orientation(self) -> str:
        value = self.tile.get('card_icon_orientation', None)
        if value in ('left', 'right', 'title'):
            return value
        return DEFAULT_ICON_ORIENTATION

    def get_available_tile_actions(self) -> List[Dict]:
        actions = super().get_available_tile_actions()
        return self.append_tile_action(actions=actions, action={
            'action_id': 'configure_tilecard_modal',
            'data_modal': '/configure_tilecard_modal',
            'data_modal_size': 'lg',
            'data_modal_request': json.dumps({'id': self.tile.get('id')}),
            'data_modal_params': json.dumps({
                'tagClass': 'configure_tilecard_modal',
                'id': 'configure_tilecard_modal',
            }),
            'data_modal_init': 'initializeConfigureTileCardModal',
            'attr_title': _('label_configure_card', default='Edit card'),
            'attr_class': 'tool interaktiv-icon-basetilestheme-tile-options',
            'visible': self.can_modify(),
        }, position=0)
