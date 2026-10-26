from zope.interface import Interface


class IGraffitiTileTabsLayer(Interface):
    """ Add-on browser layer (all views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run) """


class ITabListsProvider(Interface):
    """ Extension point: delivers the tabs of the tab lists tile.

    Adapter for (tiles page, request). What is listed is decided in code and not by editors.
    A project registers its own adapter for a more specific request layer, for example one tab
    per saved search of the current user.
    """

    def get_tabs():
        """ List of dicts, one per tab, in display order. Keys:

        * `id`: unique within the tile, plain text usable in an HTML attribute
        * `title`: label of the tab
        * `columns`: list of dicts with `id` (unique within the tab) and `title`
        * `rows`: list of dicts with `url` (link of the first column, may be empty) and `cells`,
          a dict from column id to text
        * `empty_text`: text shown when `rows` is empty

        Only rows the current user is allowed to see. An empty list hides the tile for visitors.
        """
