from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface

from openheidelberg.theme import _


class IOpenHeidelbergThemeLayer(Interface):
    """Browser layer of openheidelberg.theme."""


class IPageLayout(model.Schema):
    """Behavior schema: which layout (theme file) a TilePage is shown in.

    Empty means: the TilePage that is the default page of the site root gets the
    layout 'site-search-layout'; every other page keeps the standard theme.
    """

    page_layout = schema.Choice(
        title=_('label_page_layout', default='Page layout'),
        description=_(
            'help_page_layout',
            default='Look of this page. Empty: standard layout of the site.'
        ),
        vocabulary='openheidelberg.theme.page_layouts',
        required=False,
    )


alsoProvides(IPageLayout, IFormFieldProvider)
