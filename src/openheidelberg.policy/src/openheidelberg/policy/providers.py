from typing import Dict
from typing import List

from graffiti.tile_dashboard.adapters.boxes import CollectionBoxesProvider
from graffiti.tile_view.adapters.provider import DefaultViewsProvider
from graffiti.tile_view.interfaces import MODE_AJAX_LOAD
from graffiti.tile_view.interfaces import MODE_VIEW
from plone import api


# id of the collection that lists the latest documents in the site root (created by scripts/setup_demo_editorial_pages.py)
LATEST_DOCUMENTS_ID = 'exploring-latest'


class TaggedCollectionBoxesProvider(CollectionBoxesProvider):
    """ The boxes of a dashboard are the collections tagged with the id of the tiles page.

    The default provider takes every collection in the folder of the page. /exploring and /editing both
    live in the site root, so each of them keeps only the collections whose tag (Subject) is its own id.
    """

    def get_collections(self) -> list:
        page_id = self.context.getId()
        collections = []
        for collection in super().get_collections():
            if page_id in (collection.Subject() or ()):
                collections.append(collection)
        return collections


class ProjectViewsProvider(DefaultViewsProvider):
    """ The views of the default provider and the views of this site.

    * the number of documents (frameless view of this package)
    * the document list: the tabular view of Plone (tabular_view, with its batch navigation) of the collection
      LATEST_DOCUMENTS_ID, if that exists; the collection sorts by date and takes ten items per page
    * the folder contents of Plone (the management view of the site root); only users who may use it get a tile
      that is not empty
    """

    def get_views(self) -> List[Dict[str, str]]:
        root_url = self.navigation_root_url()
        views = super().get_views()
        views.append({
            'id': 'documents-count',
            'title': 'Number of documents',
            'description': 'How many documents the current user may see in the site. Frameless view of openheidelberg.policy.',
            'url': f'{root_url}/@@documents-count',
            'mode': MODE_VIEW,
        })
        latest = api.portal.get().get(LATEST_DOCUMENTS_ID)
        if latest is not None:
            views.append({
                'id': 'latest-documents',
                'title': 'Document list',
                'description': 'The tabular view of Plone for the collection of the latest documents, with batch navigation.',
                'url': f'{latest.absolute_url()}/@@tabular_view',
                'mode': MODE_AJAX_LOAD,
            })
        views.append({
            'id': 'folder-contents',
            'title': 'Folder contents',
            'description': 'The folder contents view of Plone for the site root, cut down to its content area via ajax_load.',
            'url': f'{root_url}/@@folder_contents',
            'mode': MODE_AJAX_LOAD,
        })
        return views
