""" Create the demo page "Entry page for authors" with the five placeholder tiles.

The page has the parts of every topic page (demo_common.topic_rows) and, between "Try it" and "How it works",
the example: an entry page for authors on a light background. At its end a button of graffiti.tile_button opens
the FAQ of the folder in a Plone modal, through its CSS class pat-plone-modal.

Usage:
    bin/instance run scripts/setup_demo_entry_page.py [site_id]

The script is idempotent: existing demo content is removed and created again.
"""
import os
import sys

import plone.api as api
from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
try:
    from plone.base.utils import get_installer  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.utils import get_installer

SITE_ID = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith('.py') else 'site'
FOLDER_ID = 'entry-authors'
# helpers shared with the other demo scripts; "bin/instance run" does not put this folder on the path
sys.path.insert(0, os.path.dirname(os.path.abspath([arg for arg in sys.argv if arg.endswith('.py')][-1])))
import demo_common  # noqa: E402
from demo_common import DOCS, card, frame, row, text_tile  # noqa: E402
PRODUCTS = [
    'graffiti.tile_listing', 'graffiti.tile_search', 'graffiti.tile_dashboard', 'graffiti.tile_view', 'graffiti.tile_tabs',
    'graffiti.tile_button',
]

INTRO = '<h2>Hello authors</h2><p>Here you find everything you need for your work.</p>'
HELP = '<h3>Questions?</h3><p>Read the FAQ or contact the editorial team.</p>'
# the explanation for visitors of the demo site, around the example page (see demo_common.topic_rows)
LEAD = (
    '<p class="lead">An entry page is the start page of an area in an intranet, here for authors.</p>'
    '<p>Editors place and move the tiles. What the tiles show is decided in code: search, numbers, lists and '
    'other views. So the page stays up to date without anybody editing it.</p>'
)
FACTS = [
    ('For', 'Authors in an intranet'),
    ('Login', 'Not needed. Signed in, authors see their own numbers.'),
    ('Packages', 'Five tiles: graffiti.tile_search, _dashboard, _listing, _tabs and _view'),
    ('Runs on', 'Plone 5.2 and 6.1'),
]
STEPS = [
    ('Search', '<p>Type a word into the search field of the example, for example <strong>policy</strong>. '
               'Results show up while you type.</p>'),
    ('Switch the lists', '<p>Switch between the tabs <em>Recently changed</em>, <em>Created by me</em> and '
                         '<em>In this folder</em>.</p>'),
    ('Open the FAQ', '<p>The button <em>FAQ: editorial work</em> opens the answers in a window, through a CSS '
                     'class on the button.</p>'),
]
EXAMPLE = (
    '<h2>The example</h2>'
    '<p>The entry page as authors see it. In the editor, the same tiles show up as placeholders.</p>'
)
HOW_IT_WORKS = (
    '<p>Each of these tiles asks an adapter for its content. A project registers its own adapters for its '
    'browser layer and keeps the tiles, views and templates as they are. Test mixins in the packages check such '
    'adapters. The FAQ button opens a window because it carries the CSS class <code>pat-plone-modal</code>.</p>'
)
DOC_LINKS = [
    (DOCS + 'docs/features/entry-pages/README.md', 'Entry pages'),
    (DOCS + 'docs/features/entry-pages/adoption.md', 'Adopt the tiles in a project'),
    (DOCS + 'docs/features/button-css-classes/README.md', 'CSS classes on buttons'),
]
# the example documents get dates of the last hours and days (in days before now), so that "recently changed"
# lists start with them; one document stays "pending", visitors do not see it
DOCUMENTS = [
    ('document-maintenance-policy', 'Policy for maintaining documents', 0.05),
    ('guide-submit-for-review', 'Guide: submitting documents for review', 0.2),
    ('templates', 'Templates for new documents', 0.6),
    ('faq-editorial-work', 'FAQ: editorial work', 1.5),
    ('style-guide', 'Style guide for writing', 4),
]
# text of the FAQ, the button at the end of the example opens it in a modal
FAQ = (
    '<h2>How do I create a new document?</h2>'
    '<p>Open the folder, choose "Add new" in the toolbar and then "Page". '
    'Give the document a title and a short description, both show up in listings and in the search.</p>'
    '<h2>When do readers see my document?</h2>'
    '<p>After it has been published. Until then only you and the editorial team see it.</p>'
    '<h2>How do I submit a document for review?</h2>'
    '<p>Choose "Submit for publication" in the state menu of the document. '
    'It then shows up in the dashboard box "Submitted for review".</p>'
    '<h2>Why does this answer open in a window?</h2>'
    '<p>The button on the entry page carries the CSS class <code>pat-plone-modal</code>. '
    'Plone opens the link target in a modal, no JavaScript of its own is needed.</p>'
)

portal = demo_common.setup_site(app, SITE_ID)  # noqa: F821 - provided by "bin/instance run"

installer = get_installer(portal, portal.REQUEST)
for product in PRODUCTS:
    if not installer.is_product_installed(product):
        installer.install_product(product)
        print('installed', product)

# only the own folder, folders of earlier versions of the demo are removed by hand
if FOLDER_ID in portal:
    api.content.delete(obj=portal[FOLDER_ID], check_linkintegrity=False)

folder = api.content.create(container=portal, type='Folder', id=FOLDER_ID, title='Entry page for authors')
page = api.content.create(container=folder, type='TilePage', id='entry', title='Entry page for authors',
                          description='A start page for authors made of tiles that fill themselves.')
folder.setDefaultPage(page.getId())
demo_common.block_portlets(folder)

for doc_id, title, _age in DOCUMENTS:
    # language and navigation flag set explicitly, so a later comparison with a working copy shows only real changes
    api.content.create(container=folder, type='Document', id=doc_id, title=title,
                       description='Example content for the folder listing.', language='en', exclude_from_nav=False)
folder['faq-editorial-work'].description = 'Answers to common questions about working with documents.'
folder['faq-editorial-work'].text = RichTextValue(FAQ, 'text/html', 'text/x-html-safe')

# one dashboard box per collection, see graffiti.tile_dashboard.adapters.boxes
SELECTION = 'plone.app.querystring.operation.selection.any'
for collection_id, title, query in [
    ('my-documents', 'My documents', [
        {'i': 'portal_type', 'o': SELECTION, 'v': ['Document']},
        {'i': 'Creator', 'o': 'plone.app.querystring.operation.string.currentUser', 'v': ''},
    ]),
    ('submitted-for-review', 'Submitted for review', [
        {'i': 'review_state', 'o': SELECTION, 'v': ['pending']},
    ]),
    ('published-documents', 'Published documents', [
        {'i': 'portal_type', 'o': SELECTION, 'v': ['Document']},
        {'i': 'review_state', 'o': SELECTION, 'v': ['published']},
    ]),
]:
    # excluded from navigation, so the folder listing tile does not list the collections;
    # the tag "todo" makes a box urgent: it turns red as soon as it has entries
    api.content.create(
        container=folder, type='Collection', id=collection_id, title=title, query=query, exclude_from_nav=True,
        subject=('todo',) if collection_id == 'submitted-for-review' else (),
    )


def band(padding_top='20px', padding_bottom='20px'):
    """ Rows of the example sit on a light background without gaps, like a page inside the page """
    return {'background_media_type': 'color', 'background_color': 'graffiti-paper',
            'margin_top': '0px', 'margin_bottom': '0px', 'padding_top': padding_top, 'padding_bottom': padding_bottom}


demo_common.ensure_colors()
example_rows = [
    row(text_tile('The example', EXAMPLE), margin_bottom='10px'),
    row(text_tile('Introduction', INTRO, gridsize=5), ('TileSearch', {'title': 'Search', 'gridsize': 7}),
        **band(padding_top='40px')),
    row(('TileDashboard', {'title': 'Dashboard'}), **band()),
    row(
        frame(row(text_tile('Heading', '<h3>Guides and templates</h3>')),
              row(('TileListing', {'title': 'Folder listing'})), gridsize=5),
        ('TileTabs', {'title': 'Lists', 'gridsize': 7}),
        **band(),
    ),
    row(
        frame(row(text_tile('Heading', '<h3>Latest changes</h3>')),
              row(('TileView', {'title': 'Recently changed', 'view_id': 'example-recent'})), gridsize=7),
        frame(row(text_tile('Help', HELP)),
              # the internal link keeps the address right behind every virtual host, the class opens it in a modal
              row(('TileButtonCT', {'title': 'FAQ', 'button_text': 'FAQ: editorial work',
                                    'button_internal_link': folder['faq-editorial-work'].UID(),
                                    'button_css_classes': 'pat-plone-modal'})),
              **demo_common.card_values(), gridsize=5),
        **band(padding_bottom='40px'),
    ),
]
demo_common.rebuild_tile_page(page, demo_common.topic_rows(
    lead=LEAD, facts=FACTS, steps=STEPS, how=HOW_IT_WORKS, docs=DOC_LINKS, extra_rows=example_rows))

# one document stays "pending": visitors do not see it, so the numbers differ from user to user
for obj in [folder] + list(folder.objectValues()):
    transition = 'submit' if obj.getId() == 'guide-submit-for-review' else 'publish'
    try:
        api.content.transition(obj=obj, transition=transition)
    except Exception:  # noqa - workflow without this transition
        pass

# dates last, every change before sets the modification date to now; the collections only feed the dashboard
for obj in [folder, page]:
    demo_common.date_back(obj)
for obj in folder.objectValues():
    if obj.portal_type == 'Collection':
        demo_common.set_modification_date(obj, demo_common.OLD_DATE)
now = DateTime()
for doc_id, _title, age in DOCUMENTS:
    demo_common.set_modification_date(folder[doc_id], now - age)

demo_common.commit()
print('created', page.absolute_url())
