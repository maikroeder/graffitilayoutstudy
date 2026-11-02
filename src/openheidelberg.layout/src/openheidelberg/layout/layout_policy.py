from typing import Optional

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from interaktiv.basetiles.views.tilepage import TilePageLayoutPolicy
from openheidelberg.layout.layouts import LAYOUT_SITE_SEARCH
from openheidelberg.layout.layouts import layout_ids
from plone.app.layout.navigation.interfaces import INavigationRoot


class OpenHeidelbergTilePageLayoutPolicy(TilePageLayoutPolicy):
    """Adds the body class "layout-<id>" to a TilePage.

    The id is the value of the field page_layout (behavior IPageLayout). A TilePage without a
    value that is the default page of the site root gets layout-site-search-layout.
    Diazo selects the theme file with this class (see static/rules.xml).
    """

    def bodyClass(self, template, view) -> str:
        # noinspection PySuperArguments
        body_class = super(OpenHeidelbergTilePageLayoutPolicy, self).bodyClass(template, view)
        layout = self.get_layout()
        if layout:
            return body_class + ' layout-' + layout
        return body_class

    def get_layout(self) -> Optional[str]:
        value = getattr(aq_base(self.context), 'page_layout', None)
        if value in layout_ids():
            return value

        parent = aq_parent(aq_inner(self.context))
        if parent is not None and INavigationRoot.providedBy(parent):
            if parent.getDefaultPage() == self.context.getId():
                return LAYOUT_SITE_SEARCH
        return None
