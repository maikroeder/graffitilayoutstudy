""" Helpers that the demo scripts share (scripts/setup_demo_*.py). Not a script of its own.

The scripts run with "bin/instance run", which does not put their folder on the module path,
so they add it themselves before they import this module.
"""
import os
from copy import deepcopy
from io import BytesIO

import interaktiv.framework as framework
import PIL.Image
import plone.api as api
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.namedfile.file import NamedBlobImage
try:
    # images with a focus point (interaktiv.image_focus), which decides the part of a header image on small screens
    from interaktiv.image_focus.file import NamedBlobImageFocus
except ImportError:
    NamedBlobImageFocus = None
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import ILocalPortletAssignmentManager, IPortletManager
from Testing.makerequest import makerequest
from zope.component import getMultiAdapter, getUtility
from zope.component.hooks import setSite
from zope.globalrequest import setRequest
from zope.interface import alsoProvides

REPO_URL = 'https://code.interaktiv.de/interaktiv/graffiti'
DOCS = REPO_URL + '/-/blob/main/'
BACKGROUND_COLORS_RECORD = 'interaktiv.basetiles.registry.backgroundcolor.IBackgroundColorsSchema.background_colors'
# light colors of the Graffiti logo for cards on the demo pages, editors find them in the background colors of tiles
COLORS = [
    {'id': 'graffiti-cream', 'title': 'Graffiti cream', 'value': '#F3EEE2'},
    {'id': 'graffiti-sky', 'title': 'Graffiti sky', 'value': '#E6EEF3'},
    {'id': 'graffiti-paper', 'title': 'Graffiti paper', 'value': '#FAF8F3'},
]
# images of the layout and of the documentation are not content: an old date keeps them out of the top of
# "recently changed" lists
IMAGES_FOLDER_ID = 'demo-images'
OLD_DATE = '2026-01-01 12:00'
# the pages of the demo itself are not content of the example intranet either: they get a date a few days back,
# so that these lists start with the example documents of the entry page (scripts/setup_demo_entry_page.py)
DEMO_PAGES_AGE = 5  # days
# tiles get this gap on both sides, so that the edges of cards line up with the text above and below
TILE_GAP = '10px'


def setup_site(app, site_id):
    """ Request, user and site as in a browser: tile values are converted by the z3c.form widgets,
    they are only found with the form layer """
    app = makerequest(app)
    alsoProvides(app.REQUEST, IPloneFormLayer)
    setRequest(app.REQUEST)
    admin = app.acl_users.getUser('admin')
    newSecurityManager(None, admin.__of__(app.acl_users))
    portal = app[site_id]
    setSite(portal)
    return portal


def link(portal, path, text):
    """ Link to an object of the site by UID, so that it works behind every virtual host """
    obj = portal.unrestrictedTraverse(path, None)
    if obj is None:
        return text
    return f'<a href="resolveuid/{api.content.get_uuid(obj=obj)}">{text}</a>'


def doc_link(path, text):
    return f'<a href="{DOCS}{path}">{text}</a>'


def ensure_colors():
    """ Add the colors of the demo pages to the background colors of the tiles, once """
    colors = list(api.portal.get_registry_record(BACKGROUND_COLORS_RECORD))
    known = {color.get('id') for color in colors}
    missing = [dict(color) for color in COLORS if color['id'] not in known]
    if missing:
        api.portal.set_registry_record(BACKGROUND_COLORS_RECORD, colors + missing)


def publish(obj):
    if api.content.get_state(obj=obj, default=None) not in (None, 'published'):
        api.content.transition(obj=obj, transition='publish')


def set_modification_date(obj, date):
    """ reindexObject() without index names sets the modification date to now, so only "modified" is reindexed """
    obj.setModificationDate(DateTime(date))
    obj.reindexObject(idxs=['modified'])


def date_back(obj, days=DEMO_PAGES_AGE):
    set_modification_date(obj, DateTime() - days)


def upload_image(portal, file_path, image_id, title, crop=None, focus=None):
    """ An image for the demo pages in the folder "demo-images", with an old date.
    crop: (left, top, right, bottom) in pixels, the part of the image to keep
    focus: (x, y) in percent, the focus point of the image, if interaktiv.image_focus is there """
    if IMAGES_FOLDER_ID not in portal:
        folder = api.content.create(container=portal, type='Folder', id=IMAGES_FOLDER_ID, title='Demo images',
                                    exclude_from_nav=True)
        publish(folder)
    folder = portal[IMAGES_FOLDER_ID]
    if image_id not in folder:
        api.content.create(container=folder, type='Image', id=image_id, title=title)
    image = folder[image_id]
    with open(file_path, 'rb') as image_file:
        data = image_file.read()
    if crop:
        output = BytesIO()
        PIL.Image.open(BytesIO(data)).crop(crop).save(output, format='PNG')
        data = output.getvalue()
    filename = os.path.basename(file_path)
    if focus and NamedBlobImageFocus is not None:
        image.image = NamedBlobImageFocus(data=data, filename=filename,
                                          extras={'focus_x': focus[0], 'focus_y': focus[1]})
    else:
        image.image = NamedBlobImage(data=data, filename=filename)
    image.reindexObject()
    for obj in (folder, image):
        set_modification_date(obj, OLD_DATE)
    return image


def block_portlets(folder):
    """ The layout of tiles pages has no room for portlet columns: the inherited navigation portlet
    would show up as soon as the folder has content and squeeze the page """
    for manager_name in ('plone.leftcolumn', 'plone.rightcolumn'):
        manager = getUtility(IPortletManager, name=manager_name, context=folder)
        assignment_manager = getMultiAdapter((folder, manager), ILocalPortletAssignmentManager)
        assignment_manager.setBlacklistStatus(CONTEXT_CATEGORY, True)


def get_or_create_tile_page(container, page_id, title, description=''):
    if page_id not in container:
        api.content.create(container=container, type='TilePage', id=page_id, title=title)
    page = container[page_id]
    page.setTitle(title)
    page.setDescription(description)
    publish(page)
    return page


def text_tile(title, html, **values):
    return ('TextCT', dict(title=title, text=RichTextValue(html, 'text/html', 'text/x-html-safe'), **values))


def card_values(color='graffiti-cream'):
    """ Values of a tile that looks like a card: background color of the Graffiti logo and padding """
    ensure_colors()
    return {'background_media_type': 'color', 'background_color': color,
            'padding_top': '25px', 'padding_bottom': '25px', 'padding_left': '30px', 'padding_right': '30px'}


def card(title, html, color='graffiti-cream', **values):
    return text_tile(title, html, **card_values(color), **values)


def frame(*rows, **values):
    """ A column with rows of its own, for a heading above a tile next to other tiles """
    return ('TileFrame', dict(rows=list(rows), **values))


def row(*tiles, **values):
    """ A row with its own values (margins, background), next to plain lists of tiles in rebuild_tile_page """
    return {'tiles': list(tiles), 'values': values}


def rebuild_tile_page(page, rows, row_values=None):
    """ Replace all rows of a tiles page: rows is a list of rows, every row a list of (portaltype, values)
    or a row(...). A value "gridsize" (1 to 12) sets the width of a tile, frame(...) puts rows into a column.
    The same steps as the checkin api of interaktiv.basetiles, so the page is published right away. """
    page.set_workingcopy()
    page.set_annotations([], edit_mode=True)
    _add_rows(page, page.get_annotations(edit_mode=True), rows, row_values or {}, TILE_GAP)
    page.set_annotations(deepcopy(page.get_annotations(edit_mode=True)), edit_mode=False)
    page.set_annotations([], edit_mode=True)
    page.increment_version()
    page.set_workingcopy(value=False)
    framework.storage.update_object(page)
    framework.locking.unlock(context=page)
    page.reindexObject()


def _add_rows(page, container, rows, row_values, gap):
    for spec in rows:
        tiles, values = (spec['tiles'], spec['values']) if isinstance(spec, dict) else (spec, {})
        elements = container['elements'] if isinstance(container, dict) else container
        tile_row = page.create_tilerow(container=container, position=len(elements), **{**row_values, **values})
        widths = []
        for portaltype, tile_values in tiles:
            tile_values = dict(tile_values)
            # rich text can not be converted by the form widgets in a console script, set it directly
            text = tile_values.pop('text', None)
            gridsize = tile_values.pop('gridsize', None)
            inner_rows = tile_values.pop('rows', None)
            tile_values.setdefault('margin_left', gap)
            tile_values.setdefault('margin_right', gap)
            tile = page.create_tile(container=tile_row, portaltype=portaltype, **tile_values)
            if text is not None:
                tile['text'] = text
            if inner_rows is not None:
                # rows and tiles in a frame bring no margins of their own, the frame has them already
                _add_rows(page, tile, inner_rows, {'margin_top': '0px', 'margin_bottom': '0px'}, '0px')
            widths.append((tile, gridsize))
        # the editor splits a row into equal parts whenever a tile is added, own widths come last
        if any(gridsize for _tile, gridsize in widths):
            for tile, gridsize in widths:
                tile['gridsize'] = gridsize


def topic_rows(lead, facts, steps, how, docs, try_intro='', extra_rows=()):
    """ The rows of a topic page, the same order on every page:
    lead text and a card with facts, "Try it" with numbered steps, extra rows (the feature itself,
    screenshots), then "How it works" and a card with links to the documentation.

    facts: list of (label, html); steps: list of (title, html), at most four; docs: list of (url, text).
    """
    facts_html = '<h3>At a glance</h3><dl class="graffiti-facts">' + ''.join(
        f'<dt>{label}</dt><dd>{value}</dd>' for label, value in facts) + '</dl>'
    docs_html = '<h3>Documentation</h3><ul class="graffiti-links">' + ''.join(
        f'<li><a href="{url}">{text}</a></li>' for url, text in docs) + '</ul>'
    step_cards = [
        card(title, f'<h3><span class="graffiti-step">{number}</span>{title}</h3>{html}')
        for number, (title, html) in enumerate(steps, start=1)
    ]
    return [
        row(text_tile('What it is', lead, gridsize=8), card('At a glance', facts_html, color='graffiti-sky', gridsize=4),
            margin_top='40px'),
        row(text_tile('Try it', '<h2>Try it</h2>' + try_intro), margin_bottom='0px'),
        row(*step_cards, margin_top='0px'),
        *extra_rows,
        row(text_tile('How it works', '<h2>How it works</h2>' + how, gridsize=8),
            card('Documentation', docs_html, color='graffiti-sky', gridsize=4), margin_bottom='50px'),
    ]


def commit():
    transaction.commit()
