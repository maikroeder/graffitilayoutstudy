from typing import Dict, List

from Acquisition import aq_inner, aq_parent
from graffiti.tile_dashboard.interfaces import IDashboardBoxesProvider
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from plone.app.contenttypes.interfaces import ICollection
from zope.component import adapter
from zope.interface import Interface, implementer

# a collection with this tag is a to-do box: it turns red as soon as it has results
URGENT_TAG = 'todo'


@implementer(IDashboardBoxesProvider)
@adapter(ITilePage, Interface)
class CollectionBoxesProvider:
    """ Default: one box for every collection that lives in the same folder as the tiles page.

    The number of a box is the number of results of its collection. Collections are evaluated
    with the permissions of the current user and can use criteria like "creator is the current
    user", so the numbers differ from user to user without any code.

    A collection tagged `todo` is an urgent box: editors decide without code which boxes turn
    red when they have entries.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_collections(self) -> list:
        folder = aq_parent(aq_inner(self.context))
        return [obj for obj in folder.objectValues() if ICollection.providedBy(obj)]

    def get_boxes(self) -> List[Dict[str, str]]:
        return [
            {
                'id': collection.getId(),
                'title': collection.Title(),
                'description': collection.Description(),
                'url': collection.absolute_url(),
                'urgent': URGENT_TAG in (collection.Subject() or ()),
            }
            for collection in self.get_collections()
        ]

    def get_counts(self) -> Dict[str, int]:
        counts = {}
        for collection in self.get_collections():
            results = collection.results(batch=False, brains=True)
            counts[collection.getId()] = getattr(results, 'actual_result_count', len(results))
        return counts
