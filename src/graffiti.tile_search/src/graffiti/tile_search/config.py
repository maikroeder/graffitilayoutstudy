from copy import deepcopy
from typing import Dict

from interaktiv.basetiles.configs.animations import ANIMATION_CLASSES
from interaktiv.basetiles.stubs import TilePermissions, AnimationClass

TILE_CLASSES: Dict[str, Dict[str, AnimationClass]] = {
    'TileSearch': {
        'animation': deepcopy(ANIMATION_CLASSES)
    }
}

PERMISSIONS: Dict[TilePermissions, str] = {
    TilePermissions.ADD: 'InteraktivTiles: Add SearchTile',
    TilePermissions.DELETE: 'InteraktivTiles: Delete SearchTile',
    TilePermissions.MOVE: 'InteraktivTiles: Move SearchTile',
    TilePermissions.MODIFY: 'InteraktivTiles: Modify SearchTile',
    TilePermissions.STYLE: 'InteraktivTiles: Style SearchTile',
}
