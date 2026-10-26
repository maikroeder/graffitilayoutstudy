""" Rebuild the front page of the demo site in English and refresh the WebMirror example.

Usage:
    bin/instance run scripts/setup_demo_front_page.py [site_id] [page_id]

The page is the default page of the site (a tiles page), or the tiles page named by page_id (id or path below the site).
Its rows are replaced: an introduction, one card per topic page and a short technical overview. Run it after
scripts/setup_demo_topic_pages.py, the cards link to these pages. The cards use a light background color that the
script adds to the background colors of the tiles. If the site has a WebMirror named "testmirror1", it gets the
example ZIP from docs/examples/ and the ID "Handbook"; its state of publication stays as it is. Running the script twice
gives the same result.
"""
import os
import sys

from plone.namedfile.file import NamedBlobFile

# "bin/instance run" puts its own options in front of the script name, the arguments follow it
SCRIPT_ARGS = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
SCRIPT_ARGS = SCRIPT_ARGS[max(i for i, arg in enumerate(SCRIPT_ARGS) if arg.endswith('.py')) + 1:]
SITE_ID = SCRIPT_ARGS[0] if SCRIPT_ARGS else 'site'
# the ZIP lies next to the scripts folder; __file__ is not the script under "bin/instance run"
SCRIPT_PATH = [arg for arg in sys.argv if arg.endswith('.py')][-1]
SCRIPTS = os.path.dirname(os.path.abspath(SCRIPT_PATH))
REPO = os.path.dirname(SCRIPTS)
EXAMPLE_ZIP = os.path.join(REPO, 'docs', 'examples', 'WebMirror_example.zip')
PAGE_ID = SCRIPT_ARGS[1] if len(SCRIPT_ARGS) > 1 else None  # id or path below the site, default: the default page of the site
TITLE = 'Welcome to Graffiti'
DESCRIPTION = 'Open source features for editorial teams that work with documents in Plone.'

sys.path.insert(0, SCRIPTS)
import demo_common  # noqa: E402 - needs the folder of the scripts on the path
from demo_common import REPO_URL  # noqa: E402

portal = demo_common.setup_site(app, SITE_ID)  # noqa: F821 - provided by "bin/instance run"

INTRO = (
    '<h2>Features for editorial teams</h2>'
    '<p>Graffiti is a Plone site with open source features for editorial teams that work with documents: '
    'they find documents, write and update them, check them and publish them. '
    'Every feature is a package that other Plone projects can adopt.</p>'
    '<p>Each topic has its own page: what it does, how to try it on this site and how it works.</p>'
)
# icon, title, text, page (path below the site, or a full address), text of the link
CARDS = [
    ('\U0001f9ed', 'Entry pages for authors',
     'A start page made of tiles that fill themselves: search, dashboard, lists and more.',
     'entry-authors', 'Open the entry page'),
    ('\U0001f4dd', 'Working copies',
     'Change a published page in a copy, compare both versions and publish the changes in one step.',
     'working-copies', 'How working copies work'),
    ('\U0001f50e', 'Exact search',
     'A search for the title of a document finds this document first.',
     'suche-demo', 'Try the search'),
    ('\U0001f4c4', 'PDF check',
     'Checks PDF files on upload whether they can be processed later.',
     'pdf-check', 'How the check works'),
    ('\U0001fa9e', 'WebMirror',
     'A small static website as a ZIP file, shown inside the Plone layout.',
     'static-websites', 'See the example'),
    ('\U0001f916', 'AI access (MCP)',
     'AI assistants search the documents of this site and read their PDF files.',
     'mcp-demo', 'Connect an assistant'),
    ('\U0001f4e6', 'Open source',
     'Every feature is a Plone package under the BSD 3-Clause License, with documentation.',
     REPO_URL, 'Source code on GitLab'),
]
UNDER_THE_HOOD = (
    '<h2>Under the hood</h2>'
    '<ul>'
    '<li>Plone 5.2.2 on Python 3.8, the move to Plone 6.1 is in progress</li>'
    '<li>Plone Classic UI with the Interaktiv Tiles Editor</li>'
    '<li>Search through Solr</li>'
    '<li>Plone on one host, the ZEO server and Solr on another one, connected through an SSH tunnel</li>'
    '</ul>'
)


def card(icon, title, text, target, link_text):
    if target.startswith('https://'):
        link = f'<a href="{target}">{link_text}</a>'
    else:
        link = demo_common.link(portal, target, link_text)
    return demo_common.card(title, f'<h3>{icon} {title}</h3><p>{text}</p><p>{link}</p>')


if PAGE_ID:
    page = portal.restrictedTraverse(PAGE_ID)
else:
    page = portal[portal.getDefaultPage()]
if page.portal_type != 'TilePage':
    raise SystemExit(f'{page.absolute_url()} is a {page.portal_type}, not a TilePage')

page.setTitle(TITLE)
page.setDescription(DESCRIPTION)
cards = [card(*entry) for entry in CARDS]
# rows of three cards; empty text tiles fill up the last row, with the same margins as the cards, so that its cards
# keep the width of the others (the spacer tile has no margins and would change the widths)
card_rows = [cards[i:i + 3] for i in range(0, len(cards), 3)]
card_rows[-1] += [demo_common.text_tile('Empty', '')] * (3 - len(card_rows[-1]))
demo_common.rebuild_tile_page(page, [
    demo_common.row(demo_common.text_tile('Introduction', INTRO), margin_top='40px'),
    *card_rows,
    demo_common.row(demo_common.text_tile('Under the hood', UNDER_THE_HOOD), margin_top='30px', margin_bottom='50px'),
], row_values={'margin_top': '10px', 'margin_bottom': '10px'})
# a page of the demo itself, not content of the example intranet: below the example documents in "recently changed"
demo_common.date_back(page)
print('front page rebuilt:', page.absolute_url())

if 'testmirror1' in portal and portal['testmirror1'].portal_type == 'WebMirror':
    if not os.path.exists(EXAMPLE_ZIP):
        raise SystemExit(f'example ZIP not found: {EXAMPLE_ZIP}')
    mirror = portal['testmirror1']
    with open(EXAMPLE_ZIP, 'rb') as zip_file:
        mirror.zipfile = NamedBlobFile(data=zip_file.read(), filename='WebMirror_example.zip', contentType='application/zip')
    mirror.webmirror_id = 'Handbook'
    mirror.extract_webmirror(force=True)
    mirror.reindexObject()
    demo_common.date_back(mirror)
    print('webmirror refreshed:', mirror.absolute_url())

demo_common.commit()
