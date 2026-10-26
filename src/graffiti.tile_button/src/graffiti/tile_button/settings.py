from typing import Optional

import plone.api as api
from interaktiv.basetiles.base_functions import check_permission
from interaktiv.basetiles.contenttypes.tilepage import ITilePage
from interaktiv.basetiles.stubs import TilePermissions

ENABLED_RECORD = 'graffiti.tile_button.css_classes_enabled'


def css_classes_enabled() -> bool:
    """ The switch in the registry, on when the record is missing """
    return bool(api.portal.get_registry_record(ENABLED_RECORD, default=True))


def offer_css_classes(tilepage: ITilePage, portal_type: Optional[str] = 'TileButtonCT') -> bool:
    """ Show the field to the current user: switched on and the user may style the tile """
    if not css_classes_enabled():
        return False
    return bool(check_permission(tilepage, portal_type, TilePermissions.STYLE))
