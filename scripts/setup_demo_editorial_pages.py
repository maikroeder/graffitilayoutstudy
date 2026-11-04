""" Rebuild the two editorial pages of the OpenHeidelberg site, /exploring and /editing, and their collections.

Usage:
    bin/instance run scripts/setup_demo_editorial_pages.py [site_id]
    (or with scripts/run_with_instance.py, see there)

Both are tiles pages in the layout "default-tiles-layout" of openheidelberg.layout: header, breadcrumbs and the
title of the page come from the layout, this script fills the tiles below them.

/exploring   a view tile with the number of documents (view "documents-count" of openheidelberg.policy), the
             search tile, a dashboard tile with one box per content type of the site and a view tile with
             the tabular view of Plone for the collection "exploring-latest" (all documents, newest first, ten
             per page, with the batch navigation of Plone; view "latest-documents") under the heading
             "Document List". Every box is a collection of the content
             type, tagged "exploring", created here in the site root. A click on a box opens the collection.
/editing     the search tile, a dashboard tile with two boxes and a view tile with the folder contents of
             Plone (view "folder-contents"). The boxes are tagged "editing": the documents the current
             user owns, and the documents to review (review state pending, tagged "todo" as well, so that the
             box turns red as soon as it has results).

The dashboard of a page shows the collections whose tag is the id of the page (TaggedCollectionBoxesProvider of
openheidelberg.policy). The numbers are those of the current user: a collection only finds what he may see.
The review box finds the pending documents the user may see; Plone has no criterion "I am to review this", so a
user without the role Reviewer sees fewer than a reviewer does.

The script registers the browser layer of openheidelberg.policy in the site (import step "browserlayer" of its
profile), because the dashboard and view providers of the policy package only apply with that layer.

The script replaces the rows of both pages and the collections with these tags, so running it twice gives the
same result.
"""
import os
import sys

import plone.api as api

# "bin/instance run" puts its own options in front of the script name, the arguments follow it
SCRIPT_ARGS = []
for arg in sys.argv[1:]:
    if not arg.startswith('-'):
        SCRIPT_ARGS.append(arg)
last_script = 0
for index in range(len(SCRIPT_ARGS)):
    if SCRIPT_ARGS[index].endswith('.py'):
        last_script = index
SCRIPT_ARGS = SCRIPT_ARGS[last_script + 1:]
SITE_ID = SCRIPT_ARGS[0] if SCRIPT_ARGS else 'Plone'

SCRIPT_PATH = [arg for arg in sys.argv if arg.endswith('.py')][-1]
SCRIPTS = os.path.dirname(os.path.abspath(SCRIPT_PATH))
sys.path.insert(0, SCRIPTS)
import demo_common  # noqa: E402 - needs the folder of the scripts on the path
from openheidelberg.layout.layouts import LAYOUT_DEFAULT_TILES  # noqa: E402
from openheidelberg.layout.interfaces import IPageLayout  # noqa: E402
from openheidelberg.policy.providers import LATEST_DOCUMENTS_ID  # noqa: E402
from openheidelberg.policy.views import NOT_DOCUMENTS  # noqa: E402

TAG_EXPLORING = 'exploring'
TAG_EDITING = 'editing'
TAG_TODO = 'todo'  # a collection with this tag turns red as soon as it has results (graffiti.tile_dashboard)
OP_ANY = 'plone.app.querystring.operation.selection.any'
OP_CURRENT_USER = 'plone.app.querystring.operation.string.currentUser'

portal = demo_common.setup_site(app, SITE_ID)  # noqa: F821 - provided by "bin/instance run"

# the providers of openheidelberg.policy are registered for its browser layer; an existing site gets the layer
# from the import step of the profile (a new install has it already)
api.portal.get_tool('portal_setup').runImportStepFromProfile('profile-openheidelberg.policy:default', 'browserlayer')


def remove_collections(tag):
    """ Delete the collections in the site root that carry the tag, so that the script can run again """
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type='Collection', Subject=tag, path={'query': '/'.join(portal.getPhysicalPath()), 'depth': 1})
    for brain in brains:
        api.content.delete(obj=brain.getObject(), check_linkintegrity=False)


def create_collection(collection_id, title, description, query, tags):
    collection = api.content.create(container=portal, type='Collection', id=collection_id, title=title,
                                    description=description, query=query, sort_on='sortable_title')
    collection.setSubject(tuple(tags))
    collection.exclude_from_nav = True
    demo_common.publish(collection)
    collection.reindexObject()
    return collection


def content_types():
    """ The portal types of the documents in the site, with the title of the type: all that has content """
    catalog = api.portal.get_tool('portal_catalog')
    types_tool = api.portal.get_tool('portal_types')
    type_ids = catalog.uniqueValuesFor('portal_type')
    found = []
    for type_id in sorted(type_ids):
        if type_id in NOT_DOCUMENTS:
            continue
        fti = types_tool.get(type_id)
        found.append((type_id, fti.Title() if fti is not None else type_id))
    return found


def heading(text):
    """ A text tile with a heading above a view tile """
    return demo_common.text_tile(text + ' heading', '<h2>{}</h2>'.format(text))


def create_latest_collection(types):
    """ The collection behind the view "latest-documents": all documents, newest first, ten per page """
    if LATEST_DOCUMENTS_ID in portal:
        api.content.delete(obj=portal[LATEST_DOCUMENTS_ID], check_linkintegrity=False)
    type_ids = []
    for type_id, type_title in types:
        type_ids.append(type_id)
    collection = api.content.create(
        container=portal, type='Collection', id=LATEST_DOCUMENTS_ID, title='Latest documents',
        description='The documents changed last',
        query=[{'i': 'portal_type', 'o': OP_ANY, 'v': type_ids}],
        sort_on='modified', sort_reversed=True, item_count=10,
    )
    collection.exclude_from_nav = True
    demo_common.publish(collection)
    collection.reindexObject()


def build_exploring():
    remove_collections(TAG_EXPLORING)
    for type_id, type_title in content_types():
        query = [{'i': 'portal_type', 'o': OP_ANY, 'v': [type_id]}]
        create_collection(
            'exploring-' + type_id.lower().replace(' ', '-'),
            type_title,
            'All documents of the type {}'.format(type_title),
            query,
            [TAG_EXPLORING],
        )
    create_latest_collection(content_types())
    rows = [
        demo_common.row(('TileView', {'title': 'Number of documents', 'view_id': 'documents-count'})),
        demo_common.row(('TileSearch', {'title': 'Search'})),
        demo_common.row(heading('Documents by content type')),
        demo_common.row(('TileDashboard', {'title': 'Documents by content type'})),
        demo_common.row(heading('Document List')),
        demo_common.row(('TileView', {'title': 'Document List', 'view_id': 'latest-documents'})),
    ]
    return rows


def build_editing():
    remove_collections(TAG_EDITING)
    create_collection(
        'editing-owner',
        'Documents I own',
        'The documents you created',
        [{'i': 'Creator', 'o': OP_CURRENT_USER, 'v': ''}],
        [TAG_EDITING],
    )
    create_collection(
        'editing-review',
        'To review',
        'Documents waiting for review',
        [{'i': 'review_state', 'o': OP_ANY, 'v': ['pending']}],
        [TAG_EDITING, TAG_TODO],
    )
    return [
        demo_common.row(('TileSearch', {'title': 'Search'})),
        demo_common.row(heading('Documents by workflow state')),
        demo_common.row(('TileDashboard', {'title': 'My documents'})),
        demo_common.row(heading('Folder content')),
        demo_common.row(('TileView', {'title': 'Folder contents', 'view_id': 'folder-contents'})),
    ]


def build_page(page_id, title, description, rows):
    page = demo_common.get_or_create_tile_page(portal, page_id, title, description)
    IPageLayout(page).page_layout = LAYOUT_DEFAULT_TILES
    demo_common.rebuild_tile_page(page, rows, row_values={'margin_top': '12px', 'margin_bottom': '12px'})
    print('page rebuilt:', page.absolute_url())


build_page('exploring', 'Exploring', 'Explore the documents of the site', build_exploring())
build_page('editing', 'Editing', 'Your documents and the documents waiting for you', build_editing())
demo_common.commit()
