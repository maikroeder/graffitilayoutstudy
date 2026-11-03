import os
from typing import List

from openheidelberg.tile_card import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

# the svg files of the card icons; the file name without ".svg" is the value stored in the tile
ICONS_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'icons')


def get_svg_icon_names() -> List[str]:
    names = []
    for file_name in sorted(os.listdir(ICONS_DIRECTORY)):
        if file_name.endswith('.svg'):
            names.append(file_name[:-len('.svg')])
    return names


def read_svg_icon(name: str) -> str:
    """Markup of the svg icon, empty if there is no icon of that name. Only names from the folder are accepted."""
    if not name or name not in get_svg_icon_names():
        return ''
    with open(os.path.join(ICONS_DIRECTORY, name + '.svg'), encoding='utf-8') as svg_file:
        return svg_file.read().strip()


# noinspection PyUnusedLocal
def svg_icons(context) -> SimpleVocabulary:
    terms = []
    for name in get_svg_icon_names():
        terms.append(SimpleTerm(value=name, token=name, title=_('label_svg_icon_' + name, default=name.capitalize())))
    return SimpleVocabulary(terms)
