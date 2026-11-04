import zope.schema as schema
from interaktiv.basetiles.contenttypes import TILE_DEFAULT_FIELDS_KEY
from interaktiv.basetiles.contenttypes import TILE_PERMISSIONS_KEY
from interaktiv.basetiles.contenttypes.basetile import BaseTile
from interaktiv.basetiles.contenttypes.basetile import IBaseTile
from interaktiv.basetiles.stubs import TilePermissions
from openheidelberg.tile_card import _
from openheidelberg.tile_card.vocabularies.orientation import DEFAULT_ICON_ORIENTATION
from plone.app.vocabularies.catalog import CatalogSource
from z3c.relationfield.schema import RelationChoice
from zope.interface import implementer
from zope.interface import taggedValue


class ITileCard(IBaseTile):
    taggedValue(TILE_PERMISSIONS_KEY, dict(
        title=TilePermissions.MODIFY,
        description=TilePermissions.MODIFY,
        image=TilePermissions.MODIFY,
        image_alt=TilePermissions.MODIFY,
        link_href=TilePermissions.MODIFY,
        link_label=TilePermissions.MODIFY,
        link_show_button=TilePermissions.MODIFY,
        card_icon=TilePermissions.MODIFY,
        card_icon_svg=TilePermissions.MODIFY,
        card_icon_orientation=TilePermissions.MODIFY,
        link_new_window=TilePermissions.MODIFY,
    ))

    taggedValue(TILE_DEFAULT_FIELDS_KEY, [])

    title = schema.TextLine(
        title=_('label_card_title', default='Title'),
        required=True,
    )

    description = schema.Text(
        title=_('label_card_description', default='Short description'),
        required=False,
    )

    image = RelationChoice(
        title=_('label_card_image', default='Image'),
        source=CatalogSource(portal_type=['Image']),
        required=False,
    )

    image_alt = schema.TextLine(
        title=_('label_card_image_alt', default='Alternative text of the image'),
        description=_(
            'help_card_image_alt',
            default='Leave empty for a purely decorative image.'
        ),
        required=False,
    )

    link_href = schema.TextLine(
        title=_('label_card_link_href', default='Link target'),
        description=_(
            'help_card_link_href',
            default='The single primary action of the card: a full URL or a path inside the site.'
        ),
        required=False,
    )

    link_show_button = schema.Bool(
        title=_('label_card_link_show_button', default='Show the action button'),
        description=_(
            'help_card_link_show_button',
            default='Off: no button; the title becomes the link and the whole card stays clickable.'
        ),
        default=True,
        required=False,
    )

    link_label = schema.TextLine(
        title=_('label_card_link_label', default='Action label'),
        required=False,
    )

    link_new_window = schema.Bool(
        title=_('label_card_link_new_window', default='Open in a new window'),
        default=False,
        required=False,
    )


    card_icon = schema.Choice(
        title=_('label_card_icon', default='Action icon'),
        description=_(
            'help_card_icon',
            default='Shown at the bottom right of the card; it takes the place of the arrow.'
        ),
        default='',
        source='interaktiv.basetiles.vocabularies.icon_fonts.icon_fonts',
        required=False,
    )

    card_icon_svg = schema.Choice(
        title=_('label_card_icon_svg', default='Vector icon'),
        description=_(
            'help_card_icon_svg',
            default='One of the vector icons of the control panel; shown beside the title.'
        ),
        default='',
        source='openheidelberg.tile_card.vocabularies.svg_icons',
        required=False,
    )
    card_icon_orientation = schema.Choice(
        title=_('label_card_icon_orientation', default='Icon position'),
        default=DEFAULT_ICON_ORIENTATION,
        source='openheidelberg.tile_card.vocabularies.icon_orientations',
        required=False,
    )


@implementer(ITileCard)
class TileCard(BaseTile):
    """A card: image, title, short description and one primary action."""
