from typing import Optional

from Products.GenericSetup.tool import SetupTool
from interaktiv.framework.products import installer

GRAFFITI_TILES = [
    'graffiti.tile_listing',
    'graffiti.tile_search',
    'graffiti.tile_dashboard',
    'graffiti.tile_tabs',
    'graffiti.tile_view',
    'graffiti.tile_button',
]


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> None:
    installer().install_products(GRAFFITI_TILES)
