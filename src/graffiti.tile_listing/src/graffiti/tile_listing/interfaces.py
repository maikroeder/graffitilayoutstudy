from zope.interface import Interface


class IGraffitiTileListingLayer(Interface):
    """ Add-on browser layer (all views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run) """


class IListingItemsProvider(Interface):
    """ Extension point: delivers the entries of the folder listing tile.

    Adapter for (tiles page, request). What is listed is decided in code and not by editors.
    A project registers its own adapter for a more specific request layer to list something
    else, for example the result of its own query.
    """

    def get_label():
        """ Short text that tells editors in the tiles editor what is listed, e.g. a folder title. """

    def get_items():
        """ List of dicts with the keys `title`, `description`, `url` and `portal_type`.

        Only entries the current user is allowed to see.
        """
