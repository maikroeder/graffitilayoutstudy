from typing import Optional, NoReturn, Union

from Products.GenericSetup.tool import SetupTool
from plone.browserlayer.utils import unregister_layer, registered_layers

BAD_LAYER = 'interaktiv.cutomworkingcopy'
BAD_LAYER_NAME = 'IInteraktivCustomWorkingcopyLayer'


# noinspection PyUnusedLocal
def upgrade(site_setup: Optional[SetupTool] = None) -> NoReturn:
    layer_names = [layer.__name__ for layer in registered_layers()]

    if BAD_LAYER_NAME in layer_names:
        unregister_layer(name=BAD_LAYER)

    if BAD_LAYER in layer_names:
        unregister_layer(name=BAD_LAYER)
