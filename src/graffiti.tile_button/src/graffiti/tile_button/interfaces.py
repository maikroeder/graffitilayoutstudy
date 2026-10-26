import zope.schema as schema
from graffiti.tile_button import _
from interaktiv.tile_button.interfaces import IInteraktivTileButtonLayer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IGraffitiTileButtonLayer(IInteraktivTileButtonLayer, IDefaultBrowserLayer):
    """ Add-on browser layer. It extends the layer of interaktiv.tile_button and the default layer,
    so the views of this package win over the views of the button tile, also over those registered
    without a layer (the dialog of the button tile), whatever the order of the layers on the request """


class IGraffitiTileButtonSettings(Interface):
    """ Registry records of this package (prefix "graffiti.tile_button") """

    css_classes_enabled = schema.Bool(
        title=_(u'label_css_classes_enabled', default=u'Offer custom CSS classes for buttons'),
        description=_(
            u'help_css_classes_enabled',
            default=u'Editors who may style the button tile set their own CSS classes. '
                    u'Switched off, the field is not offered, classes already set stay on the buttons.'
        ),
        default=True,
        required=False,
    )
