from copy import deepcopy
from typing import Dict

from interaktiv.basetiles.configs.animations import ANIMATION_CLASSES
from interaktiv.basetiles.stubs import AnimationClass
from interaktiv.basetiles.stubs import TilePermissions

TILE_CLASSES: Dict[str, Dict[str, AnimationClass]] = {
    'TileCard': {
        'animation': deepcopy(ANIMATION_CLASSES)
    }
}

PERMISSIONS: Dict[TilePermissions, str] = {
    TilePermissions.ADD: 'InteraktivTiles: Add CardTile',
    TilePermissions.DELETE: 'InteraktivTiles: Delete CardTile',
    TilePermissions.MOVE: 'InteraktivTiles: Move CardTile',
    TilePermissions.MODIFY: 'InteraktivTiles: Modify CardTile',
    TilePermissions.STYLE: 'InteraktivTiles: Style CardTile',
}
