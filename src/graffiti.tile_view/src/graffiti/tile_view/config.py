from copy import deepcopy
from typing import Dict

from interaktiv.basetiles.configs.animations import ANIMATION_CLASSES
from interaktiv.basetiles.stubs import TilePermissions, AnimationClass

TILE_CLASSES: Dict[str, Dict[str, AnimationClass]] = {
    'TileView': {
        'animation': deepcopy(ANIMATION_CLASSES)
    }
}

PERMISSIONS: Dict[TilePermissions, str] = {
    TilePermissions.ADD: 'InteraktivTiles: Add ViewTile',
    TilePermissions.DELETE: 'InteraktivTiles: Delete ViewTile',
    TilePermissions.MOVE: 'InteraktivTiles: Move ViewTile',
    TilePermissions.MODIFY: 'InteraktivTiles: Modify ViewTile',
    TilePermissions.STYLE: 'InteraktivTiles: Style ViewTile',
}
