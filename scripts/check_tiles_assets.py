"""Checks whether the CSS and JavaScript of the placeholder tiles are built and up to date.

The tiles bring their styles as LESS and their scripts as plain JavaScript. Grunt compiles both
into var/static/css/style.css and var/static/js/script.js, which the theme loads through
@@static-files. When a tile shows up without styling, one step of that chain is missing. This
script walks the chain and reports the first broken link. Plain Python, no Zope needed:

    python3 scripts/check_tiles_assets.py [buildout directory]

Exit code 1 if something is missing or out of date.
"""
import glob
import json
import os
import sys
import time

PACKAGES = [
    'graffiti.tile_listing', 'graffiti.tile_search', 'graffiti.tile_dashboard', 'graffiti.tile_tabs', 'graffiti.tile_view',
]
# one marker per package that must appear in the built files
CSS_MARKERS = {
    'graffiti.tile_listing': '.tile-listing', 'graffiti.tile_search': '.tile-search',
    'graffiti.tile_dashboard': '.tile-dashboard', 'graffiti.tile_tabs': '.tile-tabs', 'graffiti.tile_view': '.tile-view',
}
JS_MARKERS = {
    'graffiti.tile_dashboard': 'initGraffitiTileDashboard', 'graffiti.tile_tabs': 'tile-tabs-nav',
    'graffiti.tile_view': 'initializeConfigureTileViewModal',
}

results = []


def check(label, ok, detail=''):
    results.append((label, ok, detail))
    return ok


def source_dir(root, package):
    return os.path.join(root, 'src', package, 'src', *package.split('.'), 'static')


def newest_mtime(paths):
    return max((os.path.getmtime(p) for p in paths), default=0)


def age(path):
    return time.strftime('%d.%m.%Y %H:%M', time.localtime(os.path.getmtime(path)))


def main(root):
    root = os.path.abspath(root)
    print(f'Buildout-Verzeichnis: {root}')

    # 1. the packages must be checkouts under src/, that is where Grunt reads LESS and JavaScript
    for package in PACKAGES:
        less = glob.glob(os.path.join(source_dir(root, package), 'less', '*.less'))
        check(f'Quellen {package}', bool(less), f'{len(less)} LESS-Datei(en) unter src/' if less
              else 'nicht unter src/ (als Egg installiert?), Grunt findet dann kein LESS')

    # 2. the root package.json must list the packages, package-json-interaktiv-merge (npm run preinstall) writes that list
    package_json = os.path.join(root, 'package.json')
    listed = []
    if check('package.json in der Wurzel', os.path.isfile(package_json)):
        with open(package_json, encoding='utf-8') as f:
            listed = json.load(f).get('interaktiv_setup', {}).get('packages', [])
        missing = [p for p in PACKAGES if p not in listed]
        check('Pakete in interaktiv_setup.packages', not missing,
              'fehlt: ' + ', '.join(missing) + ' (npm run preinstall nicht gelaufen oder von Hand eintragen)'
              if missing else 'alle fünf eingetragen')

    # 3. npm install must have run, Grunt lives in node_modules
    grunt = os.path.join(root, 'node_modules', 'grunt-cli', 'bin', 'grunt')
    check('Grunt installiert (npm install)', os.path.isfile(grunt), '' if os.path.isfile(grunt)
          else 'node_modules/grunt-cli fehlt, npm install ist nicht gelaufen (offline?)')

    # 4. the styleguide file is written before Grunt runs
    styleguide = os.path.join(root, 'var', '_styleguide.less')
    check('var/_styleguide.less (Tiles-Styleguide)', os.path.isfile(styleguide),
          age(styleguide) if os.path.isfile(styleguide) else 'fehlt, der Styleguide-Schritt ist nicht gelaufen')

    # 5. the built files must exist, contain the tiles and be newer than their sources
    sources = []
    for package in PACKAGES:
        sources += glob.glob(os.path.join(source_dir(root, package), '**', '*.less'), recursive=True)
        sources += glob.glob(os.path.join(source_dir(root, package), '**', '*.js'), recursive=True)
    newest_source = newest_mtime(sources)

    for name, markers in (('css/style.css', CSS_MARKERS), ('js/script.js', JS_MARKERS)):
        path = os.path.join(root, 'var', 'static', name)
        if not check(f'var/static/{name} vorhanden', os.path.isfile(path), '' if os.path.isfile(path)
                     else 'nicht gebaut, Grunt ist nie gelaufen'):
            continue
        with open(path, encoding='utf-8', errors='replace') as f:
            content = f.read()
        missing = [p for p, marker in markers.items() if marker not in content]
        check(f'var/static/{name} enthält die Tiles', not missing,
              'fehlt: ' + ', '.join(missing) + ' (Datei ist ein alter Build)' if missing else 'alle enthalten')
        stale = newest_source > os.path.getmtime(path)
        check(f'var/static/{name} aktuell', not stale,
              f'gebaut {age(path)}' if not stale else f'gebaut {age(path)}, Quellen sind neuer, Grunt erneut laufen lassen')

    width = max(len(label) for label, _, _ in results)
    failed = False
    for label, ok, detail in results:
        failed = failed or not ok
        print(f"{'ok' if ok else 'FEHLT':<6} {label:<{width}}  {detail}")
    print()
    if failed:
        print('Nächster Schritt: den ersten FEHLT-Punkt beheben, dann den Build erneut anstoßen '
              '(Plone 5: bin/update_styleguide, Plone 6: bin/buildout install styleguide) und diese Prüfung wiederholen.')
    else:
        print('Ergebnis: CSS und JavaScript der Tiles sind gebaut und aktuell. Zeigt die Seite trotzdem kein Styling, '
              'liegt es an einem Cache davor oder am Theme.')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()))
