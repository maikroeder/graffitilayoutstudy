import zope.schema as schema
from graffiti.tile_dashboard import _
from interaktiv.basetiles.contenttypes import TILE_PERMISSIONS_KEY, TILE_DEFAULT_FIELDS_KEY
from interaktiv.basetiles.contenttypes.basetile import BaseTile, IBaseTile
from interaktiv.basetiles.stubs import TilePermissions
from zope.interface import implementer, taggedValue


class ITileDashboard(IBaseTile):
    taggedValue(TILE_PERMISSIONS_KEY, dict(
        title=TilePermissions.MODIFY
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


@implementer(ITileDashboard)
class TileDashboard(BaseTile):
    """ Placeholder tile: renders dashboard boxes whose numbers are loaded by JavaScript """
