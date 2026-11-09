from typing import Optional

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from openheidelberg.theme.layouts import LAYOUT_SITE_SEARCH
from openheidelberg.theme.layouts import layout_ids
from plone.app.layout.globals.layout import DefaultBodyClasses
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import getMultiAdapter


class OpenHeidelbergBodyClasses(DefaultBodyClasses):
    """Adds the body class "layout-<id>" (IBodyClassAdapter, same mechanism as interaktiv.layout).

    The id is the value of the field page_layout (behavior IPageLayout). An object without a value that is the
    default page of a navigation root (the site root) gets layout-site-search-layout.
    Diazo selects the theme file with this class (see static/rules.xml). The class is only added when the default view
    is shown, so the edit forms, the tiles editor, @@sharing and @@manage-portlets keep the frame of the site
    (site-edit-layout / site-layout).

    Plone's LayoutPolicy.bodyClass collects all IBodyClassAdapter adapters of (context, request), so this works for
    TilePages (policy of interaktiv.basetiles) and for all other content alike.
    """

    def get_classes(self, template, view):
        layout = self.get_configured_layout()
        if layout and self.is_default_view():
            return {'layout-' + layout}
        return set()

    def is_default_view(self) -> bool:
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        return bool(context_state.is_view_template())

    def get_configured_layout(self) -> Optional[str]:
        value = getattr(aq_base(self.context), 'page_layout', None)
        if value in layout_ids():
            return value

        parent = aq_parent(aq_inner(self.context))
        if parent is not None and INavigationRoot.providedBy(parent):
            if parent.getDefaultPage() == self.context.getId():
                return LAYOUT_SITE_SEARCH
        return None
