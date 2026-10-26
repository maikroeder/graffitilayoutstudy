""" Set the look of the demo site: values of the tiles styleguide, the content of the footer, the header images,
the logo and the favicon.

Usage:
    bin/instance run scripts/setup_demo_theme.py [site_id]

Everything here is data that the control panels and the editor manage as well ("Tiles-Styleguide", portlets of
the footer, "Header" in the toolbar, the logo in the site settings, the favicon in the settings of interaktiv.theme),
so they keep working. graffiti.theme only brings what these settings do not offer.
The values are written in both versions of interaktiv.basetiles:
v10 (Plone 5.2) keeps them in var/_styleguide.less, v29 (Plone 6) in the registry. Afterwards the script runs Grunt,
so style.css is built with the new values. Header images, logo and favicon come from scripts/header_images/, the header
images go into the folder "demo-images". Running the script twice gives the same result.
"""
import os
import subprocess
import sys

import OFS.Image
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.formwidget.namedfile.converter import b64encode_file
from plone.portlet.static.static import Assignment as StaticAssignment
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from Testing.makerequest import makerequest
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.globalrequest import setRequest

# "bin/instance run" puts its own options in front of the script name, the arguments follow it
SCRIPT_ARGS = [arg for arg in sys.argv[1:] if not arg.startswith('-')]
SCRIPT_ARGS = SCRIPT_ARGS[max(i for i, arg in enumerate(SCRIPT_ARGS) if arg.endswith('.py')) + 1:]
SITE_ID = SCRIPT_ARGS[0] if SCRIPT_ARGS else 'site'
# __file__ is not the script under "bin/instance run"
SCRIPT_PATH = [arg for arg in sys.argv if arg.endswith('.py')][-1]
HEADER_IMAGES = os.path.join(os.path.dirname(os.path.abspath(SCRIPT_PATH)), 'header_images')
sys.path.insert(0, os.path.dirname(os.path.abspath(SCRIPT_PATH)))
import demo_common  # noqa: E402 - needs the folder of the scripts on the path

# colors of the Graffiti logo
BLACK = '#0D0D0B'
TEXT = '#24292B'
BLUE = '#216991'
BLUE_DARK = '#174C69'
RED = '#C42716'  # red of the logo, a bit darker, so that it can carry text on white
ORANGE = '#D9912C'
CREAM = '#DAD1B9'

# LESS variable name: value, the names are the same in v10 and v29
STYLEGUIDE = {
    'global-font-family': 'Source-Sans-Pro',
    'global-font-family-bold': 'Source-Sans-Pro-Bold',
    'global-font-color': TEXT,
    'global-font-size': '17px',
    'global-font-size-tablet': '16px',
    'global-font-size-phone': '15px',
    'a-theme-font-size': '17px',
    # relative, so that it fits the smaller font sizes on tablets and phones as well
    'global-line-height': '1.65',
    'navigation_font-family': 'Source-Sans-Pro-Semibold',
    'navigation-font-family': 'Source-Sans-Pro-Semibold',
    'a-theme-color': BLUE,
    'a-theme-color-hover': RED,
    'btn-theme-primary_bg-color': BLUE,
    'btn-theme-primary_bg-color_hover': BLUE_DARK,
    'btn-theme-primary_color': '#FFFFFF',
    'btn-theme-primary_border': f'2px solid {BLUE}',
    'btn-theme-primary_border-radius': '4px',
    'btn-theme-primary_padding': '8px 18px 8px 18px',
    'heading-theme-margin-top': '32px',
    'heading-theme-margin-bottom': '12px',
    'heading-theme-margin-top-mobile': '24px',
    'heading-theme-margin-bottom-mobile': '10px',
    # text on the header images: on the dark left part of the images, without boxes
    'leadimage_information_left': '7%',
    'leadimage_information_top': '26%',
    'leadimage_title_font-size': '60px',
    'leadimage_title_font-size_mobile': '34px',
    'leadimage_title_background-color': 'transparent',
    'leadimage_description_font-size': '24px',
    'leadimage_description_font-size_mobile': '18px',
    'leadimage_description_background-color': 'transparent',
    # v29 only, graffiti.theme sets the same values on v10
    'leadimage_title_font-family': 'Lato-Bold',
    'leadimage_title_font-color': '#FFFFFF',
    'leadimage_description_font-family': 'Source-Sans-Pro',
    'leadimage_description_font-color': CREAM,
    # v29 only, v10 has no footer variables, graffiti.theme sets the same colors there
    'footer-top-background-color': '#1E2221',
    'footer-bottom-background-color': BLACK,
    'footer-font-color': CREAM,
    'footer-link-color': '#FFFFFF',
    'footer-link-color-hover': ORANGE,
    'footer-site-actions-link-color': CREAM,
    'footer-site-actions-link-color-hover': ORANGE,
}
HEADINGS = {
    # level: (font, size, line height, size mobile, line height mobile)
    'h1': ('Lato-Bold', '40px', '48px', '30px', '36px'),
    'h2': ('Lato-Bold', '30px', '38px', '24px', '30px'),
    'h3': ('Lato-Bold', '22px', '30px', '20px', '26px'),
    'h4': ('Lato-Bold', '18px', '26px', '17px', '24px'),
}
for level, (font, size, line_height, size_mobile, line_height_mobile) in HEADINGS.items():
    STYLEGUIDE.update({
        f'{level}-theme-font-family': font,
        f'{level}-theme-font-size': size,
        f'{level}-theme-line-height': line_height,
        f'{level}-theme-font-size-mobile': size_mobile,
        f'{level}-theme-line-height-mobile': line_height_mobile,
        f'{level}-theme-font-weight': '400',
        f'{level}-theme-font-weight-mobile': '400',
        f'{level}-theme-color': BLACK,
    })

REPO_URL = 'https://code.interaktiv.de/interaktiv/graffiti'
FOOTER_PORTLETS = [
    ('graffiti-about', 'Graffiti', (
        '<p>Open source features for Plone intranets: entry pages for authors, working copies, PDF checks, '
        'search and access for AI assistants. Built on the Interaktiv Tiles Editor.</p>'
        f'<p>BSD 3-Clause License. <a href="{REPO_URL}">Source code and documentation</a></p>'
    )),
    # the topic pages (scripts/setup_demo_topic_pages.py), pages that do not exist are left out
    ('graffiti-demo-pages', 'Try it', [
        ('entry-authors', 'Entry pages for authors'),
        ('working-copies', 'Working copies'),
        ('suche-demo', 'Exact search'),
        ('pdf-check', 'PDF check'),
        ('static-websites', 'WebMirror'),
        ('mcp-demo', 'AI access (MCP)'),
    ]),
    ('graffiti-built-with', 'Built with', (
        '<ul>'
        '<li><a href="https://plone.org">Plone</a>, the open source CMS</li>'
        '<li>Interaktiv Tiles Editor</li>'
        '<li><a href="https://www.interaktiv.de">Interaktiv GmbH</a></li>'
        '</ul>'
    )),
]


# page (id below the site, '' for the front page): image, header size,
# slide text: 'title' for title and description of the page, or (title, description, button title, button target)
# The topic pages of the main menu only. A folder with a default page gets the image on that default page,
# because that is the object Plone shows. interaktiv.layout shows the button of a slide only in the size "big"
# (lower in graffiti.theme).
# focus point of the header images in percent: the motifs stand on the right, the part of the image that
# narrow screens show (graffiti.theme puts the text below the image there) keeps them
HEADER_FOCUS = (80, 50)
HEADERS = {
    '': ('header-home', 'header-image-size-0',
         ('Graffiti', 'Open source features for editorial teams that work with documents in Plone',
          'Try the entry page', 'entry-authors')),
    'entry-authors': ('header-entry-authors', 'header-image-size-2', 'title'),
    'working-copies': ('header-working-copies', 'header-image-size-2', 'title'),
    'suche-demo': ('header-search', 'header-image-size-2', 'title'),
    'pdf-check': ('header-pdf-check', 'header-image-size-2', 'title'),
    'static-websites': ('header-webmirror', 'header-image-size-2', 'title'),
    'mcp-demo': ('header-mcp-demo', 'header-image-size-2', 'title'),
}


def slide_content(image):
    """ The image of a slide: interaktiv.layout 13 (Plone 6) keeps it as a relation, 5.x (Plone 5) as UID """
    from interaktiv.layout.utilities import header
    if not hasattr(header, 'RelationValue'):
        return image.UID()
    from z3c.relationfield import RelationValue
    from zope.intid.interfaces import IIntIds
    return RelationValue(getUtility(IIntIds).getId(image))


def set_header_images(portal):
    for page_id, (image_name, size, text) in HEADERS.items():
        if page_id == '':
            page_id = portal.getDefaultPage()
        if page_id not in portal:
            print('header: no page', page_id)
            continue
        page = portal[page_id]
        default_page = getattr(page.aq_base, 'getDefaultPage', lambda: None)()
        if default_page and default_page in page:
            page = page[default_page]
        image = demo_common.upload_image(portal, os.path.join(HEADER_IMAGES, image_name + '.jpg'), image_name,
                                         'Header image ' + image_name[len('header-'):], focus=HEADER_FOCUS)
        slide = {
            'content': slide_content(image),
            'title': '', 'description': '', 'button_title': '',
            'link_type': '', 'internal_link': '', 'external_link': '', 'open_in_new_window': False,
            # the images are darker on the left, where the text sits, no overlay needed
            'overlay_enabled': False, 'overlay_color': '', 'overlay_opacity': '',
        }
        if text == 'title':
            slide.update({'title': page.Title(), 'description': page.Description()})
        elif text:
            title, description, button_title, target_id = text
            slide.update({'title': title, 'description': description, 'button_title': button_title})
            if target_id in portal:
                # interaktiv.layout builds the address of the button from the UID when it shows the page
                slide.update({'link_type': 'internal_link', 'internal_link': portal[target_id].UID()})
        IAnnotations(page)['header'] = {
            'style': 'header-template-0', 'size': size, 'slides': [slide],
            'autoplay': False, 'duration': 5000, 'effect': 'fade', 'information_position': None,
        }
        # the header is an annotation, not in the catalog: no reindex, which would set the modification date
        print('header:', page.absolute_url(), image_name)


def set_styleguide_v29():
    from interaktiv.basetiles.registry.styleguide import IStyleguideSchema
    from interaktiv.basetiles.utilities.styleguide import get_styleguide_utility
    from zope.schema import getFieldsInOrder

    utility = get_styleguide_utility()
    fields = {getattr(field, 'var_name', None): field_id for field_id, field in getFieldsInOrder(IStyleguideSchema)}
    for name, value in sorted(STYLEGUIDE.items()):
        if name in fields:
            utility.set(fields[name], value)
    transaction.commit()
    utility.build()
    success, code, output = utility.run_less_compiler()
    print('grunt:', 'ok' if success else f'failed ({code})\n{output}')


def set_styleguide_v10():
    from interaktiv.basetiles.utilities.styleguide import get_styleguide_utility

    utility = get_styleguide_utility()
    # the file is written as a whole, so start from all current values
    properties = utility._extract_properties(utility.get_styleguide('all'))
    properties.update({name: value for name, value in STYLEGUIDE.items() if name in properties})
    utility.write_styleguide(properties)
    buildout_dir = os.path.dirname(os.path.dirname(utility._get_less_filepath()))
    result = subprocess.run([os.path.join(buildout_dir, 'node_modules', '.bin', 'grunt'), '--no-color'],
                            cwd=buildout_dir, capture_output=True, text=True)
    print('grunt:', 'ok' if result.returncode == 0 else f'failed ({result.returncode})\n{result.stdout[-2000:]}')


def set_logo_and_favicon(portal):
    """ The logo of the site settings, and the favicon where the favicon control panel of interaktiv.theme keeps it:
    an image "favicon.ico" in portal_skins/custom (the theme links /favicon.ico) """
    with open(os.path.join(HEADER_IMAGES, 'logo.png'), 'rb') as logo_file:
        api.portal.set_registry_record('plone.site_logo', b64encode_file('logo.png', logo_file.read()))
    with open(os.path.join(HEADER_IMAGES, 'favicon.ico'), 'rb') as icon_file:
        icon = icon_file.read()
    custom = portal.portal_skins.custom
    if 'favicon.ico' in custom.objectIds():
        custom['favicon.ico'].update_data(icon, content_type='image/x-icon')
    else:
        OFS.Image.manage_addImage(custom, 'favicon.ico', icon, content_type='image/x-icon')
    print('logo and favicon set')


def set_footer_portlets(portal):
    manager = getUtility(IPortletManager, name='plone.footerportlets', context=portal)
    mapping = getMultiAdapter((portal, manager), IPortletAssignmentMapping)
    for portlet_id, header, text in FOOTER_PORTLETS:
        if isinstance(text, list):
            text = '<ul>' + ''.join(f'<li><a href="resolveuid/{portal[obj_id].UID()}">{title}</a></li>'
                                    for obj_id, title in text if obj_id in portal) + '</ul>'
        if portlet_id in mapping:
            del mapping[portlet_id]
        mapping[portlet_id] = StaticAssignment(header=header, text=RichTextValue(text, 'text/html', 'text/x-html-safe'))
    print('footer portlets:', list(mapping.keys()))


app = makerequest(app)  # noqa: F821 - provided by "bin/instance run"
setRequest(app.REQUEST)
newSecurityManager(None, app.acl_users.getUser('admin').__of__(app.acl_users))
portal = app[SITE_ID]
setSite(portal)

set_footer_portlets(portal)
set_header_images(portal)
set_logo_and_favicon(portal)
transaction.commit()
try:
    import interaktiv.basetiles.registry.styleguide  # noqa: F401 - only in v29
except ImportError:
    set_styleguide_v10()
else:
    set_styleguide_v29()
