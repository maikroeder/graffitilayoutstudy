from typing import Optional, NoReturn

from Products.GenericSetup.tool import SetupTool
from interaktiv.workingcopy.upgrades import v0002_to_v0010


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> NoReturn:
    v0002_to_v0010.upgrade(site_setup)
