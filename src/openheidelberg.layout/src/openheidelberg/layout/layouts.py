from typing import List

from openheidelberg.layout import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

LAYOUT_SITE_SEARCH = 'site-search-layout'
LAYOUT_DEFAULT_TILES = 'default-tiles-layout'

# (id, title). The id ends up as body class "layout-<id>", which the Diazo rules select on.
LAYOUTS = [
    (LAYOUT_SITE_SEARCH, _('label_layout_site_search', default='Site search (landing page of the site root)')),
    (LAYOUT_DEFAULT_TILES, _('label_layout_default_tiles', default='Default tiles layout (landing pages)')),
]


def layout_ids() -> List[str]:
    result = []
    for layout_id, title in LAYOUTS:
        result.append(layout_id)
    return result


# noinspection PyUnusedLocal
def page_layouts_vocabulary(context) -> SimpleVocabulary:
    terms = []
    for layout_id, title in LAYOUTS:
        terms.append(SimpleTerm(value=layout_id, token=layout_id, title=title))
    return SimpleVocabulary(terms)
