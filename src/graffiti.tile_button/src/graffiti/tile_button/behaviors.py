import zope.schema as schema
from graffiti.tile_button import _
from graffiti.tile_button.css_classes import check_css_classes
from interaktiv.basetiles.contenttypes import TILE_PERMISSIONS_KEY
from interaktiv.basetiles.stubs import TilePermissions
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import taggedValue


class IButtonCssClassesBehavior(model.Schema):
    """ Adds the field for custom CSS classes to the button tile.

    The field name is the same as in a future version of interaktiv.tile_button,
    so the values stay usable when the button tile brings the field itself.
    """

    taggedValue(TILE_PERMISSIONS_KEY, dict(
        button_css_classes=TilePermissions.STYLE,
    ))

    button_css_classes = schema.TextLine(
        title=_(
            u'label_button_css_classes',
            default=u'Button: Additional CSS classes'
        ),
        description=_(
            u'help_button_css_classes',
            default=u'Separated by spaces. Letters, digits, hyphens and underscores are allowed.'
        ),
        default=u'',
        required=False,
        constraint=check_css_classes
    )


alsoProvides(IButtonCssClassesBehavior, IFormFieldProvider)


@implementer(IButtonCssClassesBehavior)
@adapter(IDexterityContent)
class ButtonCssClassesBehavior(object):
    """ Tiles are no content objects, their values live in the annotations of the tiles page """

    def __init__(self, context):
        self.context = context
