from typing import Dict, List

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_view.interfaces import IEmbeddableViewsProvider
from interaktiv.framework import form
from zExceptions import NotFound
from zope.component import getMultiAdapter

try:
    from plone.base.utils import safe_text  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.utils import safe_text


class ConfigureModalView(BrowserView):
    """ Settings of the view tile: pick one of the registered views """

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

    def get_views(self) -> List[Dict[str, str]]:
        provider = getMultiAdapter((self.context, self.request), IEmbeddableViewsProvider)
        selected = self.tile.get('view_id') or ''
        return [dict(entry, selected=(entry['id'] == selected)) for entry in provider.get_views()]
