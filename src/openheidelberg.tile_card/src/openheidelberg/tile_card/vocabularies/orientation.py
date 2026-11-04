from typing import List

from interaktiv.framework import vocabulary
from interaktiv.framework.vocabulary import VocabularyOption
from openheidelberg.tile_card import _
from zope.schema.vocabulary import SimpleVocabulary

DEFAULT_ICON_ORIENTATION: str = 'title'

ICON_ORIENTATIONS: List[VocabularyOption] = [
    {
        'id': 'left',
        'title': _('label_icon_orientation_left', default='Left of the text'),
        'value': 'left'
    },
    {
        'id': 'right',
        'title': _('label_icon_orientation_right', default='Right of the text'),
        'value': 'right'
    },
    {
        'id': 'title',
        'title': _('label_icon_orientation_title', default='Beside the title, text below'),
        'value': 'title'
    },
]


# noinspection PyUnusedLocal
def icon_orientations(context) -> SimpleVocabulary:
    return vocabulary.create_vocabulary(ICON_ORIENTATIONS)
