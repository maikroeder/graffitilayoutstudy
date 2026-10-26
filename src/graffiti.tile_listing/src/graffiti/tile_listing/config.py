from copy import deepcopy
from typing import Dict

from interaktiv.basetiles.configs.animations import ANIMATION_CLASSES
from interaktiv.basetiles.stubs import TilePermissions, AnimationClass

TILE_CLASSES: Dict[str, Dict[str, AnimationClass]] = {
    'TileListing': {
        'animation': deepcopy(ANIMATION_CLASSES)
    }
}

PERMISSIONS: Dict[TilePermissions, str] = {
    TilePermissions.ADD: 'InteraktivTiles: Add ListingTile',
    TilePermissions.DELETE: 'InteraktivTiles: Delete ListingTile',
    TilePermissions.MOVE: 'InteraktivTiles: Move ListingTile',
    TilePermissions.MODIFY: 'InteraktivTiles: Modify ListingTile',
    TilePermissions.STYLE: 'InteraktivTiles: Style ListingTile',
}
