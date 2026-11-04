from Products.CMFPlone.PloneControlPanel import PloneControlPanel
from openheidelberg.tile_card import _

CATEGORY_ID = 'MosaikTiles'


def add_control_panel_category() -> None:
    """Own section "Mosaik Tiles" in the site setup overview, as interaktiv.basetiles does for "Interaktiv Tiles"
    (patches/plone_control_panel.py): the categories are a class attribute of the control panel tool."""
    categories = PloneControlPanel.group['site']
    for category_id, title in categories:
        if category_id == CATEGORY_ID:
            return
    categories.append((CATEGORY_ID, _('label_controlpanel_category_mosaik_tiles', default='Mosaik Tiles')))


add_control_panel_category()
