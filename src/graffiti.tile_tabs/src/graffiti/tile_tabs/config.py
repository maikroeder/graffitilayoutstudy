from copy import deepcopy
from typing import Dict

from interaktiv.basetiles.configs.animations import ANIMATION_CLASSES
from interaktiv.basetiles.stubs import TilePermissions, AnimationClass

TILE_CLASSES: Dict[str, Dict[str, AnimationClass]] = {
    'TileTabs': {
        'animation': deepcopy(ANIMATION_CLASSES)
    }
}

PERMISSIONS: Dict[TilePermissions, str] = {
    TilePermissions.ADD: 'InteraktivTiles: Add TabsTile',
    TilePermissions.DELETE: 'InteraktivTiles: Delete TabsTile',
    TilePermissions.MOVE: 'InteraktivTiles: Move TabsTile',
    TilePermissions.MODIFY: 'InteraktivTiles: Modify TabsTile',
    TilePermissions.STYLE: 'InteraktivTiles: Style TabsTile',
}
