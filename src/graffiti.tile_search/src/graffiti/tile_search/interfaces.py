from zope.interface import Interface


class IGraffitiTileSearchLayer(Interface):
    """ Add-on browser layer (all views and viewlets register against this layer will appear on
    your Plone site only when the add-on installer has been run) """


class ISearchTileSettings(Interface):
    """ Extension point: tells the search tile where to search.

    Adapter for (tiles page, request). Where the search goes is decided in code and not by
    editors. A project registers its own adapter for a more specific request layer, for
    example to use its own search page or to restrict the search to a part of the site.
    """

    def get_search_url():
        """ URL the form is submitted to (GET). The search term is sent as `SearchableText`. """

    def get_livesearch_url():
        """ URL that delivers the live results for the pattern `pat-livesearch` as JSON.

        Same format as `@@ajax-search` of Plone. `None` switches the live results off.
        """

    def get_parameters():
        """ Dict of additional, fixed parameters that are sent with the search as hidden inputs,

        for example `{'path': '/site/documents'}`. They are not applied to the live results.
        """

    def get_search_parameter_name():
        """ Name of the request parameter that carries the search term, `SearchableText` for Plone.

        A project with its own search page returns the name its page expects. Not applied to
        the live results, they always use the format of `@@ajax-search`.
        """
