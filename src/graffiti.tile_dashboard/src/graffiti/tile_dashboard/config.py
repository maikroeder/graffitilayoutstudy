from copy import deepcopy
from typing import Dict

from interaktiv.basetiles.configs.animations import ANIMATION_CLASSES
from interaktiv.basetiles.stubs import TilePermissions, AnimationClass

TILE_CLASSES: Dict[str, Dict[str, AnimationClass]] = {
    'TileDashboard': {
        'animation': deepcopy(ANIMATION_CLASSES)
    }
}

PERMISSIONS: Dict[TilePermissions, str] = {
    TilePermissions.ADD: 'InteraktivTiles: Add DashboardTile',
    TilePermissions.DELETE: 'InteraktivTiles: Delete DashboardTile',
    TilePermissions.MOVE: 'InteraktivTiles: Move DashboardTile',
    TilePermissions.MODIFY: 'InteraktivTiles: Modify DashboardTile',
    TilePermissions.STYLE: 'InteraktivTiles: Style DashboardTile',
}
