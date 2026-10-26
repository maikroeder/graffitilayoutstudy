from typing import Optional

from Products.GenericSetup.tool import SetupTool
from interaktiv.framework.products import installer


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> None:
    installer().install_products(['graffiti.contenttypes'])
