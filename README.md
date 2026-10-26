# graffitilayoutstudy

Code behind the paper *Graffiti Layout Study* (`~/Writing/GraffitiLayoutStudyPaper`, thinking in
`~/Writing/Workspaces/graffiti-layout-study-paper`): a fresh Graffiti installation with the complete
Interaktiv Tiles Editor package set, and the OpenHeidelberg layout produced with it from a set of
design guidelines.

## Layout

```
install.sh                all steps of the install howto, in order
bootstrap.sh              howto step 2: venv + bin/buildout + upstream Graffiti checkout, symlinks into src/
stage.cfg                 howto step 3 (gitignored): extends buildout.d/standalone.cfg, Apple Silicon pins
_stage-settings.cfg       local instance settings (port 8080, admin/admin)
buildout.cfg              plain entry point -> buildout.d/standalone.cfg
buildout.d/               copied from Graffiti main (Plone 5.2.2, Python 3.8)
  base/sources.cfg        mr.developer pins for all interaktiv.* packages; develop/eggs incl. openheidelberg.*
package.json, Gruntfile.js, pre.js, post.js    node side of the update_styleguide buildout part
src/openheidelberg.layout        site layout (theme, tile page layouts, design tokens)
src/openheidelberg.tile_events   OpenHeidelberg-specific tile
upstream/graffiti         (gitignored) Graffiti main; src/graffiti.*, interaktiv.cronjob, interaktiv.workingcopy
                          are symlinked into src/ by bootstrap.sh
docs/design-guidelines.md placeholder for the input design guidelines
```

## Install

Follows `~/selfhosted/howtos/graffiti-plone-buildout-fresh-install.md` (and, for Apple Silicon,
`zope-buildout-apple-silicon-compile-fixes.md` in the same folder):

```
./install.sh              # = howto steps 0, 2, 3 check, 4, 5
bin/instance fg           # step 7; then add a Plone site at http://localhost:8080/manage
./bin/test --all          # step 6
```

Prerequisites (howto step 0): `python3.8` on PATH (`.python-version` pins pyenv 3.8.18), Xcode command
line tools, `node`/`npm`, SSH access to `code.interaktiv.de` (the `interaktiv.*` sources and the npm helper
`package-json-interaktiv-merge` are cloned from there).

Deviations from the howto, which assumes a git worktree of the Graffiti repo itself: this is a separate
repo, so step 1 is replaced by cloning Graffiti into `upstream/graffiti` and symlinking its packages into
`src/`; `stage.cfg` omits `nope.paperwork`; `package.json` carries the howto's step 5a `get_package` fix;
`_stage-settings.cfg` is local (port 8080) rather than Graffiti's stage settings. Solr is not set up (the
howto's "Not covered").

## Base choice

Everything is based on Graffiti `main`: Plone 5.2.2 on Python 3.8, tiles editor `interaktiv.basetiles`
v10 (decided 2026-10-26). This base includes `graffiti.tile_listing`, `.tile_search`, `.tile_dashboard`,
`.tile_view` and `.tile_tabs`. The Plone 6.1.2 branch (`21170-migrate_to_plone6`, basetiles v29) is not used.
Status of this buildout: assembled from Graffiti `main`'s own configs, **not yet run**.

## Naming

All site-specific code goes into packages prefixed `openheidelberg.` (e.g. `openheidelberg.layout`,
`openheidelberg.tile_events`). Add a new one: create `src/openheidelberg.<name>`, then add it to the
`eggs`, `eggs-test` and `develop` lists in `buildout.d/base/sources.cfg`.
