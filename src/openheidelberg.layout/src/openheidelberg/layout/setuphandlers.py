from zope.interface import implementer

try:
    from plone.base.interfaces import INonInstallable  # Plone 6
except ImportError:  # Plone 5.2
    from Products.CMFPlone.interfaces import INonInstallable


@implementer(INonInstallable)
class HiddenProfiles(object):

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'openheidelberg.layout:uninstall',
        ]
