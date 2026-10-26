from zope.interface import Interface


class IGraffitiTileDashboardLayer(Interface):
    """ Add-on browser layer (all views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run) """


class IDashboardBoxesProvider(Interface):
    """ Extension point: delivers the boxes of the dashboard tile.

    Adapter for (tiles page, request). Which boxes a dashboard shows is decided in code and
    not by editors. A project registers its own adapter for a more specific request layer to
    deliver other boxes, for example depending on the roles or groups of the current user.
    """

    def get_boxes():
        """ List of dicts with the keys `id`, `title`, `description` and `url`.

        Optional key `urgent` (bool): the box is highlighted (red, marked "to do") as soon as
        its number is above zero. Every box decides that for itself, default is False.

        Is used to render the tile, so it has to be cheap. Do not calculate numbers here.
        """

    def get_counts():
        """ Dict that maps the id of every box to its number for the current user.

        Is called by JavaScript after the page has been rendered.
        """
