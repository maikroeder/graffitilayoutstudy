from typing import Dict, List

from Acquisition import aq_inner, aq_parent
from graffiti.tile_listing.interfaces import IListingItemsProvider
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from plone import api
from zope.component import adapter
from zope.interface import Interface, implementer


@implementer(IListingItemsProvider)
@adapter(ITilePage, Interface)
class FolderItemsProvider:
    """ Default: the content of the folder the tiles page lives in, in folder order.

    The tiles page itself and content that is excluded from navigation are skipped. Editors
    hide content from the listing with the standard setting "exclude from navigation".
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_folder(self):
        return aq_parent(aq_inner(self.context))

    def get_label(self) -> str:
        return self.get_folder().Title()

    def get_items(self) -> List[Dict[str, str]]:
        brains = api.content.find(
            context=self.get_folder(),
            depth=1,
            sort_on='getObjPositionInParent'
        )
        own_uid = api.content.get_uuid(obj=self.context)
        return [
            {
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'portal_type': brain.portal_type,
            }
            for brain in brains
            if brain.UID != own_uid and not brain.exclude_from_nav
        ]
