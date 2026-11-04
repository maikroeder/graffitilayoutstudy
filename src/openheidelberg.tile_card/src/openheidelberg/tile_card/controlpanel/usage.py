from typing import Dict
from typing import List

from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations

# Where the tile data lives: annotations of the TilePage, 'view' (published) and 'edit' (working copy), each
# {'tiles': [row, ...]}; rows, frames and tiles nest through the key 'elements'. The walker only reads (the
# get_annotations of TilePage creates missing keys, which would be a write on a GET) and only follows 'elements'
# (the key 'parent' points back up).
SVG_FIELD = 'card_icon_svg'
MODES = (('view', 'published'), ('edit', 'working copy'))


def _walk(elements: list, found: set) -> None:
    for element in elements or []:
        if not hasattr(element, 'get'):
            continue
        name = element.get(SVG_FIELD)
        if name:
            found.add(name)
        sub_elements = element.get('elements')
        if sub_elements:
            _walk(sub_elements, found)


def find_svg_icon_usage(context) -> Dict[str, List[Dict[str, str]]]:
    """Icon name -> the pages (title, url, mode) whose tiles use it. Reads every TilePage of the site, unrestricted."""
    catalog = getToolByName(context, 'portal_catalog')
    usage = {}
    for brain in catalog.unrestrictedSearchResults(portal_type='TilePage'):
        page = brain._unrestrictedGetObject()
        annotations = IAnnotations(page)
        for key, label in MODES:
            data = annotations.get(key)
            if not hasattr(data, 'get'):
                continue
            found = set()
            _walk(data.get('tiles'), found)
            for name in sorted(found):
                usage.setdefault(name, []).append({
                    'title': brain.Title or brain.getPath(),
                    'url': brain.getURL(),
                    'mode': label,
                })
    return usage
