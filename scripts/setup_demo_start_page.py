""" Rebuild the start page of the OpenHeidelberg site: three sections with three cards each.

Usage:
    bin/instance run scripts/setup_demo_start_page.py [site_id] [page_id]

The page is the default page of the site (a tiles page), or the tiles page named by page_id (id or path below the
site). It is shown by the layout "site-search-layout" of openheidelberg.theme: the hero (logo, title, subtitle) and the
search come from the layout, this script fills the content below them: every section is a frame (a column with its own
rows) with a heading and one row of three cards (openheidelberg.tile_card). The box around the cards is not set here:
the stylesheet of the card package shows every frame that contains cards as a section. The title and the description of
the page become the title and the subtitle of the hero. The texts are the placeholders of docs/showcase.html in
graffiti.theme. Its rows are replaced, running the script twice gives the same result.
"""
import os
import sys

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
PAGE_ID = SCRIPT_ARGS[1] if len(SCRIPT_ARGS) > 1 else None  # id or path below the site, default: the default page

SCRIPT_PATH = [arg for arg in sys.argv if arg.endswith('.py')][-1]
SCRIPTS = os.path.dirname(os.path.abspath(SCRIPT_PATH))
sys.path.insert(0, SCRIPTS)
import demo_common  # noqa: E402 - needs the folder of the scripts on the path

TITLE = 'Tiles'
DESCRIPTION = 'A showcase of the Graffiti tiles editor'
SECTION_COUNT = 3
CARDS_PER_SECTION = 3
# the bundled svg icons of openheidelberg.tile_card, in the order of the nine cards
CARD_ICONS = ['grid', 'document', 'image', 'calendar', 'people', 'folder', 'globe', 'book', 'star']

portal = demo_common.setup_site(app, SITE_ID)  # noqa: F821 - provided by "bin/instance run"


def card(number):
    return ('TileCard', {
        'title': 'Showcase {} Title'.format(number),
        'description': 'Showcase {} Description'.format(number),
        'link_href': '/',
        'link_show_button': False,
        'card_icon_svg': CARD_ICONS[(number - 1) % len(CARD_ICONS)],
        'card_icon_orientation': 'title',
    })


def section(index):
    """ A frame with a heading and a row of cards, the box of a section """
    first = (index - 1) * CARDS_PER_SECTION + 1
    cards = []
    for number in range(first, first + CARDS_PER_SECTION):
        cards.append(card(number))
    heading = demo_common.text_tile(
        'Section {} heading'.format(index),
        '<h2>Showcase Section {}</h2>'.format(index),
    )
    return demo_common.frame(
        [heading],
        cards,
        margin_left='0px', margin_right='0px',
    )


if PAGE_ID:
    page = portal.restrictedTraverse(PAGE_ID)
else:
    page = portal[portal.getDefaultPage()]
if page.portal_type != 'TilePage':
    raise SystemExit('{} is a {}, not a TilePage'.format(page.absolute_url(), page.portal_type))

page.setTitle(TITLE)
page.setDescription(DESCRIPTION)
rows = []
for index in range(1, SECTION_COUNT + 1):
    rows.append(demo_common.row(section(index)))
demo_common.rebuild_tile_page(page, rows, row_values={'margin_top': '12px', 'margin_bottom': '12px'})
print('start page rebuilt:', page.absolute_url())
demo_common.commit()
