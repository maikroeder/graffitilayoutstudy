from importlib.metadata import version

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from graffiti.tile_button import logger
from graffiti.tile_button.css_classes import split_css_classes
from interaktiv.tile_button.views.view import TileButtonCTView

# One copy of the template of interaktiv.tile_button per major version, changed in one place: the original
# expression of the class attribute of the link is wrapped in get_button_classes().
TEMPLATES = {
    '10': 'templates/view_10.pt',  # Plone 5.2
    '15': 'templates/view_15.pt',  # Plone 6.1
}
TILE_BUTTON_VERSION = version('interaktiv.tile_button')
TEMPLATE = TEMPLATES.get(TILE_BUTTON_VERSION.split('.')[0])
if TEMPLATE is None:
    logger.warning(
        'No template for interaktiv.tile_button %s, the button tile renders without custom CSS classes. '
        'Add a copy of its template to graffiti.tile_button, see the README.', TILE_BUTTON_VERSION)


class TileButtonView(TileButtonCTView):
    """ The button tile of interaktiv.tile_button with custom CSS classes on the link.

    tests/test_css_classes.py renders this view and the original one, so a change of the original template
    after an update of interaktiv.tile_button shows up as a failing test.
    """
    if TEMPLATE:
        template = ViewPageTemplateFile(TEMPLATE)

    def get_button_classes(self, classes: str = 'button') -> str:
        """ The classes of the original template plus the custom ones """
        return ' '.join(classes.split() + split_css_classes(self.tile.get('button_css_classes')))
