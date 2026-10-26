from interaktiv.basetiles.base_functions import tile_classes_installer
from interaktiv.basetiles.base_functions import tile_classes_uninstaller
from interaktiv.basetiles.base_functions import tile_installer
from interaktiv.basetiles.base_functions import tile_uninstaller
from openheidelberg.tile_card import _
from openheidelberg.tile_card.config import TILE_CLASSES
from zope.interface import implementer

try:
    from plone.base.interfaces import INonInstallable  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.interfaces import INonInstallable


# noinspection PyUnusedLocal
def setup_after(context):
    tile_installer(
        tile_id='openheidelberg_tile_card',
        label=_('label_TileCard', default='Card'),
        portaltype='TileCard',
        icon='interaktiv-icon-basetilestheme-image',
        config='openheidelberg.tile_card.config'
    )
    tile_classes_installer(TILE_CLASSES)


# noinspection PyUnusedLocal
def uninstall_after(context):
    tile_uninstaller('openheidelberg_tile_card')
    tile_classes_uninstaller(TILE_CLASSES)


@implementer(INonInstallable)
class HiddenProfiles(object):

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'openheidelberg.tile_card:uninstall',
        ]
