from graffiti.tile_dashboard import _
from graffiti.tile_dashboard.config import TILE_CLASSES
from interaktiv.basetiles.base_functions import (
    tile_installer, tile_classes_installer,
    tile_classes_uninstaller, tile_uninstaller
)
try:
    from plone.base.interfaces import INonInstallable  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


# noinspection PyUnusedLocal
def setup_after(context):

    tile_installer(
        tile_id='graffiti_tile_dashboard',
        label=_('label_TileDashboard', default='Dashboard'),
        portaltype='TileDashboard',
        icon='interaktiv-icon-basetilestheme-news',
        config='graffiti.tile_dashboard.config'
    )

    tile_classes_installer(TILE_CLASSES)


# noinspection PyUnusedLocal
def uninstall_after(context):
    tile_uninstaller('graffiti_tile_dashboard')

    tile_classes_uninstaller(TILE_CLASSES)


@implementer(INonInstallable)
class HiddenProfiles(object):

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'graffiti.tile_dashboard:uninstall',
        ]
