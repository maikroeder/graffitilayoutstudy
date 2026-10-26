from typing import Dict, List

from Acquisition import aq_inner, aq_parent
from graffiti.tile_tabs import _
from graffiti.tile_tabs.interfaces import ITabListsProvider
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from plone import api
from zope.component import adapter
from zope.i18n import translate
from zope.interface import Interface, implementer

LIMIT = 10


@implementer(ITabListsProvider)
@adapter(ITilePage, Interface)
class DefaultTabsProvider:
    """ Default: three tabs built from the catalog, the same three columns in each.

    * recently changed items the current user may see (without the site itself)
    * items created by the current user (empty for visitors)
    * the content of the folder the tiles page lives in
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_folder(self):
        return aq_parent(aq_inner(self.context))

    def get_columns(self) -> List[Dict[str, str]]:
        return [
            {'id': 'title', 'title': self.translate(_('label_column_title', default='Title'))},
            {'id': 'type', 'title': self.translate(_('label_column_type', default='Type'))},
            {'id': 'modified', 'title': self.translate(_('label_column_modified', default='Changed'))},
        ]

    def get_tabs(self) -> List[Dict]:
        own_uid = api.content.get_uuid(obj=self.context)
        return [
            self.tab('recent', _('label_tab_recent', default='Recently changed'), self.rows(
                sort_on='modified', sort_order='descending',
                skip=lambda brain: brain.portal_type == 'Plone Site',
            )),
            self.tab('mine', _('label_tab_mine', default='Created by me'), self.rows_of_current_user()),
            self.tab('folder', _('label_tab_folder', default='In this folder'), self.rows(
                path={'query': '/'.join(self.get_folder().getPhysicalPath()), 'depth': 1},
                sort_on='getObjPositionInParent',
                skip=lambda brain: brain.UID == own_uid or brain.exclude_from_nav,
            )),
        ]

    def tab(self, tab_id: str, title, rows: List[Dict]) -> Dict:
        return {
            'id': tab_id,
            'title': self.translate(title),
            'columns': self.get_columns(),
            'rows': rows,
            'empty_text': self.translate(_('label_no_rows', default='No entries')),
        }

    def rows_of_current_user(self) -> List[Dict]:
        if api.user.is_anonymous():
            return []
        return self.rows(Creator=api.user.get_current().getId(), sort_on='modified', sort_order='descending')

    def rows(self, skip=None, **query) -> List[Dict]:
        catalog = api.portal.get_tool('portal_catalog')
        rows = []
        for brain in catalog(**query):
            if skip is not None and skip(brain):
                continue
            rows.append({
                'url': brain.getURL(),
                'cells': {
                    'title': brain.Title,
                    'type': self.translate(brain.Type),
                    'modified': api.portal.get_localized_time(datetime=brain.modified, long_format=True),
                },
            })
            if len(rows) >= LIMIT:
                break
        return rows

    def translate(self, message) -> str:
        return translate(message, context=self.request)
