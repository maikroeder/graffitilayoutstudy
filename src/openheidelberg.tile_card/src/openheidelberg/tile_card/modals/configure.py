from typing import Dict
from typing import List

import plone.api as api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interaktiv.basetiles.vocabularies.icon_fonts import get_selectable_icon_groups
from interaktiv.framework import form
from openheidelberg.tile_card.vocabularies.orientation import DEFAULT_ICON_ORIENTATION
from openheidelberg.tile_card.vocabularies.orientation import ICON_ORIENTATIONS
from openheidelberg.tile_card.vocabularies.svg_icons import get_svg_icons
from zExceptions import NotFound

try:
    from plone.base.utils import safe_text  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.utils import safe_text


class ConfigureModalView(BrowserView):
    """Settings of the card tile; saved through the generic update_content API."""

    template = ViewPageTemplateFile('templates/configure.pt')

    def __call__(self) -> str:
        self.tile = {}
        success, msg = form.handle_required_fields(['id'], self.request.form)
        if not success:
            self.request.response.setStatus(status=400, reason=safe_text(msg))
            return ''

        tile_id = self.request.form.get('id')
        self.tile = self.context.get_annotation_data_by_id(tile_id, True)
        if not self.tile:
            raise NotFound(f'No tile with id "{tile_id}" found.')

        return self.template(self)

    def get_selected_image_uid(self) -> str:
        ref = self.tile.get('image', None)
        if not ref or ref.isBroken():
            return ''
        obj = ref.to_object
        if obj is None:
            return ''
        return obj.UID()

    def get_images(self) -> List[Dict[str, str]]:
        selected = self.get_selected_image_uid()
        result = []
        brains = api.content.find(portal_type='Image', sort_on='sortable_title')
        for brain in brains[:500]:
            uid = brain.UID
            result.append({
                'uid': uid,
                'title': brain.Title or brain.getId,
                'selected': uid == selected,
            })
        return result

    def get_selectable_icon_groups(self) -> list:
        local_roles = api.user.get_roles(obj=self.context)
        return get_selectable_icon_groups(local_roles=local_roles)

    @staticmethod
    def get_icon_orientations() -> list:
        return ICON_ORIENTATIONS

    def get_selected_icon_orientation(self) -> str:
        value = self.tile.get('card_icon_orientation', None)
        if value in ('left', 'right', 'title'):
            return value
        return DEFAULT_ICON_ORIENTATION

    def get_svg_icons(self) -> list:
        """The svg icons of the registry for the picker: name and markup, the chosen one marked."""
        selected = self.tile.get('card_icon_svg', '') or ''
        result = []
        for name, markup in get_svg_icons().items():
            result.append({'name': name, 'svg': markup, 'selected': name == selected})
        return result
