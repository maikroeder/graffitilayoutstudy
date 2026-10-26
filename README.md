# graffitilayoutstudy

Code behind the paper *Graffiti Layout Study* (`~/Writing/GraffitiLayoutStudyPaper`, thinking in
`~/Writing/Workspaces/graffiti-layout-study-paper`): a fresh Graffiti installation with the complete
Interaktiv Tiles Editor package set, and the OpenHeidelberg layout produced with it from a set of
design guidelines.

## Layout

```
install.sh                all steps of the install howto, in order
bootstrap.sh              howto step 2: venv + bin/buildout
stage.cfg                 howto step 3 (gitignored, written by install.sh): extends standalone.cfg, Apple Silicon pins
_stage-settings.cfg       local instance settings (port 8080, admin/admin)
buildout.cfg              plain entry point -> buildout.d/standalone.cfg
buildout.d/               from Graffiti main (Plone 5.2.2, Python 3.8)
  base/sources.cfg        mr.developer pins for all interaktiv.* packages; develop/eggs incl. openheidelberg.*
package.json, Gruntfile.js, pre.js, post.js    node side of the update_styleguide buildout part
src/graffiti.*, src/interaktiv.cronjob, src/interaktiv.workingcopy
                          vendored from Graffiti main, commit c3740f1 (2026-10-26); do not edit
src/interaktiv.*          all other tiles editor packages: checked out by mr.developer, gitignored
src/openheidelberg.policy        policy package of the site (structure of graffiti.policy); installs Graffiti + tile_card
src/openheidelberg.tile_card     card tile (image, title, short description, one action)
docs/design-guidelines.md placeholder for the input design guidelines
```

## Install

Follows `~/selfhosted/howtos/graffiti-plone-buildout-fresh-install.md` (and, for Apple Silicon,
`zope-buildout-apple-silicon-compile-fixes.md` in the same folder). Step numbers below are the howto's.

### Prerequisites (step 0)

- `python3.8` on PATH. With pyenv: `pyenv install 3.8.18`; the committed `.python-version` selects it here.
- Xcode command line tools (C extensions are compiled).
- `node` and `npm` (the `update_styleguide` buildout part runs npm and grunt).
- SSH access to `code.interaktiv.de`: the ~25 `interaktiv.*` packages and the npm helper
  `package-json-interaktiv-merge` are cloned from there. Check: `ssh -T git@code.interaktiv.de`.
- Optional, for the PDF check (`graffiti.pdfcheck`, its steps are skipped without them):
  `brew install poppler qpdf` (Linux: `apt install poppler-utils qpdf`).

### Run

```
git clone <this repo> graffitilayoutstudy && cd graffitilayoutstudy
./install.sh
```

`install.sh` runs, in order:

1. Step 0: checks the prerequisites above and stops with a message if one is missing.
2. Step 2, `bootstrap.sh`: recreates `.venv` with `python3.8`, installs `requirements.txt` (the pinned
   Plone 5.2.2 requirements), runs `buildout bootstrap` to create `bin/buildout`.
3. Step 3: writes `stage.cfg` if missing. It is gitignored on purpose (machine-specific). It extends
   `buildout.d/standalone.cfg` and `_stage-settings.cfg` and pins the Apple Silicon versions.
4. Step 4, Apple Silicon macOS only: `pip install --no-deps` of `zope.container`, `AccessControl`, `cffi`,
   `Pillow` into `.venv`. buildout's own installer cannot use wheels, so the `[versions]` pins alone fail
   at compile time.
5. Step 5: `bin/buildout -c stage.cfg`. The first run clones the `interaktiv.*` repos into `src/` and
   runs `update_styleguide` (npm install, grunt). It takes a while.

If the buildout stalls on `Downloading .../solr-8.11.1.tgz` (archive.apache.org is slow, the file is 208 MB):
stop it with Ctrl-C, copy the tarball from an earlier Graffiti install into the download cache under the
name buildout expects (the md5 of the URL), then continue with `./bin/buildout -c stage.cfg`:

```
mkdir -p download-cache
cp ~/Code/graffiti/<any install>/download-cache/3b942b5c16993be56e7cd90982de3158 download-cache/
```

If a step fails, the howto's sections 5 and 5a cover the known cases (compile errors for the four pinned
packages; npm cache owned by root; `package-json-interaktiv-merge` missing from `node_modules`).

### After the install

```
bin/instance fg           # step 7: starts Zope on http://localhost:8080
```

1. Open `http://localhost:8080/manage` (admin / admin, from `_stage-settings.cfg`) and add a Plone site.
2. In the site's Site Setup, Add-ons, activate `openheidelberg.policy`. It depends on `graffiti.policy`,
   which installs all Graffiti and tiles editor add-ons, and on `openheidelberg.tile_card`.
3. Add a "Tiles-Seite" from the toolbar's Add menu to try the editor.
4. Optional demo content, with the instance stopped (a running instance holds the ZODB lock):
   `bin/instance run scripts/setup_demo_theme.py`, then `setup_demo_topic_pages.py`, then
   `setup_demo_front_page.py` (the front page links to the topic pages). Each script documents its
   arguments in its docstring.

Tests (step 6): `./bin/test --all`, or one package: `./bin/test -s graffiti.contenttypes -v`.

Deviations from the howto, which assumes a git worktree of the Graffiti repo itself: this is a separate
repo, so step 1 is replaced by vendoring Graffiti's `src/` into this repo's `src/`; `stage.cfg` omits
`nope.paperwork`; `package.json` carries the howto's step 5a `get_package` fix; `_stage-settings.cfg` is
local (port 8080) rather than Graffiti's stage settings. Solr is not set up (the howto's "Not covered").

## Base choice

Everything is based on Graffiti `main`: Plone 5.2.2 on Python 3.8, tiles editor `interaktiv.basetiles`
v10 (decided 2026-10-26). This base includes `graffiti.tile_listing`, `.tile_search`, `.tile_dashboard`,
`.tile_view` and `.tile_tabs`. The Plone 6.1.2 branch (`21170-migrate_to_plone6`, basetiles v29) is not used.
Status of this buildout: assembled from Graffiti `main`'s own configs, **not yet run**.

## Naming

All site-specific code goes into packages prefixed `openheidelberg.` (e.g. `openheidelberg.policy`,
`openheidelberg.tile_card`). Add a new one: create `src/openheidelberg.<name>`, then add it to the
`eggs`, `eggs-test` and `develop` lists in `buildout.d/base/sources.cfg`.
