import zope.schema as schema
from graffiti.tile_search import _
from interaktiv.basetiles.contenttypes import TILE_PERMISSIONS_KEY, TILE_DEFAULT_FIELDS_KEY
from interaktiv.basetiles.contenttypes.basetile import BaseTile, IBaseTile
from interaktiv.basetiles.stubs import TilePermissions
from zope.interface import implementer, taggedValue


class ITileSearch(IBaseTile):
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


@implementer(ITileSearch)
class TileSearch(BaseTile):
    """ Placeholder tile: renders the site search with live results """
