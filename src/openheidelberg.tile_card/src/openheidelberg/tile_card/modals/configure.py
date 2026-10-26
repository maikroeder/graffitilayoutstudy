from typing import Dict
from typing import List

import plone.api as api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from interaktiv.framework import form
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
