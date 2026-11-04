import os
from typing import Dict
from typing import List

from openheidelberg.tile_card import _
from plone.registry import Record
from plone.registry import field
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

# The svg icons of the card tile live in the registry (control panel "Card tile SVG icons"): a dict from the
# name, which is stored in the tile, to the sanitised markup. As long as nothing was saved there, the icons bundled
# with the package (static/icons/*.svg) are used.
REGISTRY_RECORD = 'openheidelberg.tile_card.svg_icons'

ICONS_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'icons')


def get_bundled_svg_icons() -> Dict[str, str]:
    """The icons shipped with the package: file name without ".svg" -> markup."""
    icons = {}
    for file_name in sorted(os.listdir(ICONS_DIRECTORY)):
        if file_name.endswith('.svg'):
            with open(os.path.join(ICONS_DIRECTORY, file_name), encoding='utf-8') as svg_file:
                icons[file_name[:-len('.svg')]] = svg_file.read().strip()
    return icons


def get_svg_icons() -> Dict[str, str]:
    """All icons the editors can choose from: the registry record if it exists, else the bundled ones."""
    registry = queryUtility(IRegistry)
    stored = registry.get(REGISTRY_RECORD) if registry is not None else None
    if stored is None:
        return get_bundled_svg_icons()
    icons = {}
    for name, markup in stored.items():
        icons[name] = markup
    return icons


def set_svg_icons(icons: Dict[str, str]) -> None:
    """Writes the icons to the registry; the record is created with the first call."""
    registry = queryUtility(IRegistry)
    value = {}
    for name, markup in icons.items():
        value[name] = markup
    if REGISTRY_RECORD in registry.records:
        registry[REGISTRY_RECORD] = value
        return
    icon_field = field.Dict(
        title='Card tile SVG icons',
        description='Name -> svg markup, edited in the control panel of the card tile.',
        key_type=field.TextLine(),
        value_type=field.Text(),
    )
    registry.records[REGISTRY_RECORD] = Record(icon_field, value)


def get_svg_icon_names() -> List[str]:
    return list(get_svg_icons().keys())


def read_svg_icon(name: str) -> str:
    """Markup of the svg icon, empty if there is no icon of that name."""
    if not name:
        return ''
    return get_svg_icons().get(name, '').strip()


# noinspection PyUnusedLocal
def svg_icons(context) -> SimpleVocabulary:
    terms = []
    for name in get_svg_icon_names():
        terms.append(SimpleTerm(value=name, token=name, title=_('label_svg_icon_' + name, default=name.capitalize())))
    return SimpleVocabulary(terms)
