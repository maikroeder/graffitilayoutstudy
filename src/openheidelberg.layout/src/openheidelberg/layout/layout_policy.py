from typing import Optional

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from interaktiv.basetiles.views.tilepage import TilePageLayoutPolicy
from openheidelberg.layout.layouts import LAYOUT_SITE_SEARCH
from openheidelberg.layout.layouts import layout_ids
from plone.app.layout.globals.layout import LayoutPolicy
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import getMultiAdapter


class LayoutClassMixin:
    """Adds the body class "layout-<id>" to the body class of the policy it is mixed into.

    The id is the value of the field page_layout (behavior IPageLayout). An object without a value that is the
    default page of a navigation root (the site root) gets layout-site-search-layout.
    Diazo selects the theme file with this class (see static/rules.xml). The class is only added in view mode, so the
    edit forms and the tiles editor of the page keep the frame of the site (site-edit-layout).

    Mixed into the policy of the TilePage (OpenHeidelbergTilePageLayoutPolicy) and into the policy of every other
    content object (OpenHeidelbergLayoutPolicy); both are registered under the view name "plone_layout".
    """

    def bodyClass(self, template, view) -> str:
        # noinspection PyUnresolvedReferences
        body_class = super().bodyClass(template, view)
        layout = self.get_layout()
        if layout:
            return body_class + ' layout-' + layout
        return body_class

    def is_view_mode(self) -> bool:
        raise NotImplementedError

    def is_default_view(self) -> bool:
        """True when the request shows the default view of the object (not an edit form, the sharing page, ...)."""
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        return bool(context_state.is_view_template())

    def get_layout(self) -> Optional[str]:
        layout = self.get_configured_layout()
        if layout and self.is_view_mode():
            return layout
        return None

    def get_configured_layout(self) -> Optional[str]:
        value = getattr(aq_base(self.context), 'page_layout', None)
        if value in layout_ids():
            return value

        parent = aq_parent(aq_inner(self.context))
        if parent is not None and INavigationRoot.providedBy(parent):
            if parent.getDefaultPage() == self.context.getId():
                return LAYOUT_SITE_SEARCH
        return None


class OpenHeidelbergTilePageLayoutPolicy(LayoutClassMixin, TilePageLayoutPolicy):
    """TilePages: keeps the body classes of interaktiv.basetiles (view-mode, edit-mode, is-tilepage, ...).

    View mode here is: not edit mode and the default view is shown. basetiles sets view-mode on every TilePage view that
    is not edit mode, also on @@sharing or @@manage-portlets of the page; those must not get the layout.
    """

    def is_view_mode(self) -> bool:
        return not self.get_edit_mode() and self.is_default_view()


class OpenHeidelbergLayoutPolicy(LayoutClassMixin, LayoutPolicy):
    """All other content: the policy of plone.app.layout plus the layout class.

    These objects have no edit-mode class; view mode is when the request shows the default view of the object
    (not an edit form, a control panel or another view).
    """

    def is_view_mode(self) -> bool:
        return self.is_default_view()
