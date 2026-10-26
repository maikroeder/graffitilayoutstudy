import zope.schema as schema
from graffiti.tile_view import _
from interaktiv.basetiles.contenttypes import TILE_PERMISSIONS_KEY, TILE_DEFAULT_FIELDS_KEY
from interaktiv.basetiles.contenttypes.basetile import BaseTile, IBaseTile
from interaktiv.basetiles.stubs import TilePermissions
from zope.interface import implementer, taggedValue


class ITileView(IBaseTile):
    taggedValue(TILE_PERMISSIONS_KEY, dict(
        title=TilePermissions.MODIFY,
        view_id=TilePermissions.MODIFY,
    ))

    taggedValue(TILE_DEFAULT_FIELDS_KEY, [])

    title = schema.TextLine(
        title=_(
            'label_title',
            default='Title'
        ),
        description='',
        required=True
    )

    # the id of an entry of IEmbeddableViewsProvider. A plain text field on purpose: the value
    # conversion of the tiles api expects a list for choice fields, text passes on every version.
    view_id = schema.TextLine(
        title=_(
            'label_view_id',
            default='View'
        ),
        description=_(
            'help_view_id',
            default='Which of the registered views this tile embeds.'
        ),
        required=False
    )


@implementer(ITileView)
class TileView(BaseTile):
    """ Tile that embeds a registered view """
