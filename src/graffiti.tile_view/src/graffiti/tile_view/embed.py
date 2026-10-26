""" Renders a registered view for the view tile """
from typing import Dict, Optional
from urllib.parse import urlsplit, urlencode, parse_qsl

import lxml.html
from graffiti.tile_view import logger
from graffiti.tile_view.interfaces import IEmbeddableViewsProvider, MODE_AJAX_LOAD, MODE_VIEW
from plone.subrequest import subrequest
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest

# ids of the page frame that must not appear twice on a page
FRAME_IDS = ('content', 'content-core', 'portal-column-content', 'main-container', 'visual-portal-wrapper')


class EmbedError(Exception):
    """ the view could not be rendered for embedding """


def get_view_entry(context, request, view_id: str) -> Optional[Dict[str, str]]:
    """ The registered entry with the given id, None if it is not (or no longer) registered """
    if not view_id:
        return None
    provider = getMultiAdapter((context, request), IEmbeddableViewsProvider)
    for entry in provider.get_views():
        if entry.get('id') == view_id:
            return entry
    return None


def path_for_subrequest(url: str, request=None) -> str:
    """ Turns an absolute url into the path plone.subrequest expects: relative to the virtual root,
    query string included. """
    request = request or getRequest()
    parts = urlsplit(url)
    # physicalPathFromURL keeps a query string as part of the last segment, so strip it first
    physical = list(request.physicalPathFromURL(parts._replace(query='', fragment='').geturl()))
    virtual_root = list(request.get('VirtualRootPhysicalPath', ('',)))
    if physical[:len(virtual_root)] == virtual_root:
        physical = physical[len(virtual_root):]
    path = '/' + '/'.join(segment for segment in physical if segment)
    if parts.query:
        path += '?' + parts.query
    return path


def with_ajax_load(url: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    query['ajax_load'] = '1'
    return parts._replace(query=urlencode(query)).geturl()


def without_ajax_load(url: str) -> str:
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if key != 'ajax_load']
    return parts._replace(query=urlencode(query)).geturl()


def extract_content(html: str) -> str:
    """ The content area of a page rendered with ajax_load, without the frame ids """
    tree = lxml.html.fromstring(html)
    for element_id in ('content-core', 'content'):
        found = tree.get_element_by_id(element_id, None)
        if found is not None:
            break
    else:
        found = tree.find('body') if tree.tag == 'html' else tree
        if found is None:
            found = tree
    for element in found.iter():
        if element.get('id') in FRAME_IDS:
            del element.attrib['id']
        # links and forms inside the page carry ajax_load on, they must lead to the normal page
        for attribute in ('href', 'action'):
            value = element.get(attribute)
            if value and 'ajax_load' in value:
                element.set(attribute, without_ajax_load(value))
    inner = (found.text or '') + ''.join(lxml.html.tostring(child, encoding='unicode') for child in found)
    return inner.strip()


def render_entry(entry: Dict[str, str], request=None) -> str:
    """ Renders the registered view as HTML fragment. Raises EmbedError if that fails. """
    request = request or getRequest()
    mode = entry.get('mode', MODE_VIEW)
    url = entry['url']
    if mode == MODE_AJAX_LOAD:
        url = with_ajax_load(url)
    elif mode != MODE_VIEW:
        raise EmbedError(f'unknown mode "{mode}" for view "{entry.get("id")}"')

    response = subrequest(path_for_subrequest(url, request))
    status = response.getStatus()
    if status != 200:
        raise EmbedError(f'view "{entry.get("id")}" answered with status {status}')
    body = response.getBody()
    if isinstance(body, bytes):
        body = body.decode('utf-8', 'replace')

    if mode == MODE_AJAX_LOAD:
        return extract_content(body)

    if '<html' in body[:500].lower():
        # a frameless view must not deliver a whole page, the developer registered the wrong mode
        raise EmbedError(f'view "{entry.get("id")}" renders a whole page, register it with mode "ajax_load"')
    return body.strip()


def render_view(context, request, view_id: str) -> str:
    entry = get_view_entry(context, request, view_id)
    if entry is None:
        raise EmbedError(f'view "{view_id}" is not registered')
    try:
        return render_entry(entry, request)
    except EmbedError:
        raise
    except Exception as e:  # noqa - surfaced to the caller as EmbedError
        logger.exception('embedding view "%s" failed', view_id)
        raise EmbedError(str(e)) from e
