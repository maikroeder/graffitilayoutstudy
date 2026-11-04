import re

from lxml import etree

SVG_NS = 'http://www.w3.org/2000/svg'

NAME_PATTERN = re.compile(r'^[a-z0-9][a-z0-9_-]{0,39}$')

# Only plain drawing: no script, no style, no links, no embedded objects.
ALLOWED_ELEMENTS = frozenset([
    'svg', 'g', 'path', 'circle', 'ellipse', 'rect', 'line', 'polyline', 'polygon',
])

ALLOWED_ATTRIBUTES = frozenset([
    'viewBox', 'd', 'cx', 'cy', 'r', 'rx', 'ry', 'x', 'y', 'x1', 'y1', 'x2', 'y2', 'width', 'height', 'points',
    'fill', 'fill-rule', 'fill-opacity', 'clip-rule', 'opacity',
    'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit',
    'stroke-dasharray', 'stroke-dashoffset', 'stroke-opacity', 'transform',
    'preserveAspectRatio', 'aria-hidden', 'focusable',
])

MAX_BYTES = 20000


class SvgError(ValueError):
    """The markup is not an acceptable icon; the message says why."""


def check_name(name: str) -> str:
    name = (name or '').strip()
    if not NAME_PATTERN.match(name):
        raise SvgError('Name: lower-case letters, digits, "-" and "_", at most 40 characters, starting with a letter or digit.')
    return name


def sanitize_svg(markup: str) -> str:
    """Returns the cleaned markup of one inline icon, or raises SvgError.

    The result is a single <svg> with a viewBox and without width and height (the card sets the size), with aria-hidden
    and focusable=false. Elements and attributes outside the lists above are rejected, not dropped silently, so
    that what the admin sees in the preview is what is stored. Colour: use currentColor so that the icon takes the
    colour of the card.
    """
    markup = (markup or '').strip()
    if not markup:
        raise SvgError('The svg markup is empty.')
    if len(markup.encode('utf-8')) > MAX_BYTES:
        raise SvgError('The svg is larger than %d bytes.' % MAX_BYTES)
    if '<!' in markup.replace('<!--', ''):
        raise SvgError('A DOCTYPE or entity declaration is not allowed.')
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, remove_comments=True,
                             remove_pis=True, huge_tree=False)
    try:
        root = etree.fromstring(markup.encode('utf-8'), parser)
    except etree.XMLSyntaxError as error:
        raise SvgError('Not well-formed xml: %s' % error)
    if root.tag != '{%s}svg' % SVG_NS and root.tag != 'svg':
        raise SvgError('The root element must be <svg xmlns="http://www.w3.org/2000/svg">.')

    for element in root.iter():
        if not isinstance(element.tag, str):
            raise SvgError('Comments and processing instructions are not allowed.')
        namespace, _, local = element.tag[1:].partition('}') if element.tag.startswith('{') else ('', '', element.tag)
        if namespace not in ('', SVG_NS) or local not in ALLOWED_ELEMENTS:
            raise SvgError('Element <%s> is not allowed (allowed: %s).' % (local, ', '.join(sorted(ALLOWED_ELEMENTS))))
        if element is not root and local == 'svg':
            raise SvgError('Nested <svg> is not allowed.')
        if element.text and element.text.strip():
            raise SvgError('Text inside <%s> is not allowed.' % local)
        for attribute, value in element.attrib.items():
            if attribute not in ALLOWED_ATTRIBUTES:
                raise SvgError('Attribute "%s" on <%s> is not allowed.' % (attribute, local))
            lowered = value.lower()
            if 'url(' in lowered or 'javascript:' in lowered or 'data:' in lowered or '<' in value:
                raise SvgError('Attribute "%s" on <%s> contains a reference or markup.' % (attribute, local))

    if not root.get('viewBox'):
        raise SvgError('The root <svg> needs a viewBox, for example viewBox="0 0 24 24".')
    for attribute in ('width', 'height'):
        if attribute in root.attrib:
            del root.attrib[attribute]

    # rebuild the root so that the namespace and the fixed attributes are always the same
    result = etree.Element('{%s}svg' % SVG_NS, nsmap={None: SVG_NS})
    result.set('aria-hidden', 'true')
    result.set('focusable', 'false')
    for attribute, value in root.attrib.items():
        result.set(attribute, value)
    result.text = None
    for child in root:
        result.append(child)
    return etree.tostring(result, encoding='unicode')
