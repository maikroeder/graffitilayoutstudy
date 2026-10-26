"""Checks whether a Plone environment provides what the five placeholder tiles need.

The tiles graffiti.tile_listing, tile_search, tile_dashboard, tile_tabs and tile_view only rely on
a small part of interaktiv.basetiles (and one helper of interaktiv.framework). This script names
every piece and reports what is missing, so a project can check its own environment before it
installs the packages. It does not need the tile packages themselves.

Without a database (imports and signatures only):

    bin/zopepy scripts/check_tiles_requirements.py

With a Plone site (adds the views, portal types and the tiles registered in the editor):

    bin/instance run scripts/check_tiles_requirements.py <site_id>

Exit code 1 if something required is missing.
"""
import importlib
import sys

try:
    from importlib.metadata import version as dist_version
except ImportError:  # Python 3.7
    from pkg_resources import get_distribution

    def dist_version(name):
        return get_distribution(name).version

REQUIRED_IMPORTS = [
    # (module, attributes the tiles use)
    ('interaktiv.basetiles.base_functions', [
        'tile_installer', 'tile_uninstaller', 'tile_classes_installer', 'tile_classes_uninstaller',
        'get_registered_tiles',
    ]),
    ('interaktiv.basetiles.stubs', ['TilePermissions', 'AnimationClass']),
    ('interaktiv.basetiles.configs.animations', ['ANIMATION_CLASSES']),
    ('interaktiv.basetiles.contenttypes', ['TILE_PERMISSIONS_KEY', 'TILE_DEFAULT_FIELDS_KEY']),
    ('interaktiv.basetiles.contenttypes.basetile', ['BaseTile', 'IBaseTile']),
    ('interaktiv.basetiles.contenttypes.tilepage', ['ITilePage', 'TilePage']),
    ('interaktiv.basetiles.views.basetile', ['BaseTileView']),
    ('interaktiv.basetiles.behaviors.background', ['IBackgroundBehavior']),
    ('interaktiv.basetiles.behaviors.padding', ['IPaddingBehavior']),
    ('interaktiv.basetiles.behaviors.vertical_align', ['IVerticalAligmentBehavior']),
    ('interaktiv.basetiles.behaviors.anchor', ['IAnchorBehavior']),
    ('interaktiv.framework', ['form']),  # form.handle_required_fields, modal of the view tile
    ('plone.subrequest', ['subrequest']),  # view tile
    ('lxml.html', ['fromstring']),  # view tile
]
# only needed to run the tests and contract tests of the packages
OPTIONAL_IMPORTS = [
    ('interaktiv.basetiles.test', ['InteraktivBasetilesTestCase']),
    ('interaktiv.framework', ['TestLayer']),
    ('interaktiv.framework.test', ['TestCase']),
]
BASE_TILE_VIEW_MEMBERS = [
    'template', 'template_edit_mode', 'jsinit', 'view_classes', 'get_tile_view_macro',
    'get_available_tile_actions', 'append_tile_action', 'is_tile_empty', 'get_edit_mode', 'can_modify',
]
TILE_PAGE_MEMBERS = ['render', 'create_tilerow', 'create_tile', 'get_annotations', 'set_annotations', 'update_element']
# browser views the tiles and their editor modal expect on a tiles page
VIEW_NAMES = ['tile_view', 'tile_edit', 'background_options', 'update_content', 'configure_tile_modal']
PORTAL_TYPES = ['TilePage', 'TileRowCT']
# used by static/js of the tiles, check them in the browser console of a tiles page: typeof <name>
JS_FUNCTIONS = ['ModalClass', 'refreshTiles', 'jQuery']

results = []


def check(label, ok, detail='', required=True):
    results.append((label, ok, detail, required))


def check_import(module_name, names, required):
    try:
        module = importlib.import_module(module_name)
    except Exception as e:  # noqa - report every failure
        check(module_name, False, str(e).splitlines()[0], required)
        return None
    missing = [name for name in names if not hasattr(module, name)]
    check(module_name, not missing, 'fehlt: ' + ', '.join(missing) if missing else ', '.join(names), required)
    return module


def check_versions():
    for name in ('Products.CMFPlone', 'interaktiv.basetiles', 'interaktiv.framework', 'plone.subrequest', 'lxml'):
        try:
            check('Version ' + name, True, dist_version(name), required=False)
        except Exception:  # noqa
            check('Version ' + name, False, 'nicht installiert', required=name != 'interaktiv.framework')
    check('Python', True, sys.version.split()[0], required=False)


def check_members():
    try:
        from interaktiv.basetiles.views.basetile import BaseTileView
        missing = [m for m in BASE_TILE_VIEW_MEMBERS if not hasattr(BaseTileView, m)]
        check('BaseTileView', not missing, 'fehlt: ' + ', '.join(missing) if missing else ', '.join(BASE_TILE_VIEW_MEMBERS))
    except Exception as e:  # noqa
        check('BaseTileView', False, str(e))
    try:
        from interaktiv.basetiles.contenttypes.tilepage import TilePage
        missing = [m for m in TILE_PAGE_MEMBERS if not hasattr(TilePage, m)]
        check('TilePage', not missing, 'fehlt: ' + ', '.join(missing) if missing else ', '.join(TILE_PAGE_MEMBERS))
    except Exception as e:  # noqa
        check('TilePage', False, str(e))
    try:
        from interaktiv.framework import form
        check('interaktiv.framework.form', hasattr(form, 'handle_required_fields'), 'handle_required_fields')
    except Exception as e:  # noqa
        check('interaktiv.framework.form', False, str(e))


def check_site(site):
    """ Needs a running Zope app: views, portal types and the tiles registered in the editor. """
    from interaktiv.basetiles.base_functions import get_registered_tiles
    from interaktiv.basetiles.contenttypes.tilepage import ITilePage
    from zope.component import getSiteManager
    from zope.component.hooks import setSite
    from zope.interface import Interface
    from zope.publisher.interfaces.browser import IDefaultBrowserLayer

    setSite(site)
    types_tool = site.portal_types
    for portal_type in PORTAL_TYPES:
        check('Portaltyp ' + portal_type, types_tool.getTypeInfo(portal_type) is not None)

    # the views are registered for the default layer or for the browser layer of interaktiv.basetiles
    layers = [IDefaultBrowserLayer]
    try:
        from interaktiv.basetiles.interfaces import IInteraktivBasetilesLayer
        layers.append(IInteraktivBasetilesLayer)
    except ImportError:
        pass
    registry = getSiteManager().adapters
    for name in VIEW_NAMES:
        found = any(registry.lookup((ITilePage, layer), Interface, name) is not None for layer in layers)
        check('View @@' + name, found, '' if found else 'für keinen bekannten Browser-Layer registriert')

    registered = get_registered_tiles()
    ids = sorted(tile.get('id', '?') for tile in registered)
    check('Tiles im Editor registriert', bool(registered), ', '.join(ids), required=False)
    check('Rahmen-Tile (TileFrame) im Editor', any('frame' in tile_id for tile_id in ids),
          'wird von den Platzhalter-Tiles nicht gebraucht, nur zur Einordnung', required=False)


def main():
    check_versions()
    for module_name, names in REQUIRED_IMPORTS:
        check_import(module_name, names, required=True)
    for module_name, names in OPTIONAL_IMPORTS:
        check_import(module_name, names, required=False)
    check_members()

    app = globals().get('app')
    if app is not None:
        # bin/instance run passes: interpreter -c <script> [args]
        site_id = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith('.py') else None
        site = app.unrestrictedTraverse(site_id, None) if site_id else None
        if site is None:
            check('Plone-Site', False, 'Site-ID angeben: bin/instance run scripts/check_tiles_requirements.py <site_id>',
                  required=False)
        else:
            check_site(site)
    else:
        check('Plone-Site', True, 'ohne Datenbank geprüft, für Views und Registry: bin/instance run ... <site_id>',
              required=False)

    width = max(len(label) for label, _, _, _ in results)
    failed = False
    for label, ok, detail, required in results:
        if ok:
            state = 'ok'
        elif required:
            state = 'FEHLT'
            failed = True
        else:
            state = 'fehlt (optional)'
        print(f'{state:<17} {label:<{width}}  {detail}')
    print()
    print('Im Browser auf einer Tiles-Seite prüfen (Konsole): ' + ', '.join(f'typeof {name}' for name in JS_FUNCTIONS))
    print('Ergebnis: ' + ('es fehlt etwas, siehe FEHLT' if failed else 'alle Voraussetzungen erfüllt'))
    return 1 if failed else 0


if __name__ == '__main__' or globals().get('app') is not None:
    sys.exit(main())
