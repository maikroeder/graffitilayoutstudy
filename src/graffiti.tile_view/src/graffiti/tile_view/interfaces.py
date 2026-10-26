from zope.interface import Interface


class IGraffitiTileViewLayer(Interface):
    """ Add-on browser layer (all views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run) """


MODE_VIEW = 'view'
MODE_AJAX_LOAD = 'ajax_load'
MODES = (MODE_VIEW, MODE_AJAX_LOAD)


class IEmbeddableViewsProvider(Interface):
    """ Extension point: the views that editors may embed with the view tile.

    Adapter for (tiles page, request). Only views registered here can be embedded, editors
    choose from this list. A project registers its own adapter for a more specific request
    layer to offer its own views.

    Two modes:

    * `view`: the url renders a fragment without the page frame (no <html>, no main template),
      the tile inserts it as it is. This is the clean way, comparable to the `embedded` view
      of EasyForm.
    * `ajax_load`: the url renders a normal Plone page. The tile requests it with
      `ajax_load=1`, so Plone leaves out navigation, columns, footer and toolbar, and cuts out
      the content area. Meant as an interim solution for views that have no frameless variant yet.
    """

    def get_views():
        """ List of dicts with the keys `id`, `title`, `description`, `url` and `mode`.

        `id` is unique within the list, `url` is absolute, `mode` is `view` or `ajax_load`.
        """
