#!/usr/bin/env bash
# Runs ~/selfhosted/howtos/graffiti-plone-buildout-fresh-install.md, steps 0 and 2-5, in order.
# Re-run safe: bootstrap.sh recreates .venv; stage.cfg is only written if missing.
set -e

echo ">> Step 0: prerequisites"
command -v "${PYTHON:-python3.8}" >/dev/null || { echo "python3.8 not on PATH (pyenv install 3.8.18; pyenv local 3.8.18)"; exit 1; }
command -v node >/dev/null && command -v npm >/dev/null || { echo "node/npm required (update_styleguide part)"; exit 1; }
ssh -o BatchMode=yes -T git@code.interaktiv.de || { echo "SSH access to code.interaktiv.de failed"; exit 1; }
for tool in pdftoppm qpdf
do
    command -v "$tool" >/dev/null || echo "NOTE: $tool not found; the PDF check (graffiti.pdfcheck) skips its steps. macOS: brew install poppler qpdf"
done

echo ">> Step 2: bootstrap venv + bin/buildout"
./bootstrap.sh

echo ">> Step 3: stage.cfg"
if [ ! -f stage.cfg ]
then
    echo "   writing stage.cfg (gitignored, machine-specific)"
    cat > stage.cfg <<'EOFSTAGE'
# Generated per graffiti-plone-buildout-fresh-install.md (step 3); gitignored, machine-specific.
[buildout]
extends =
    buildout.d/standalone.cfg
    buildout.d/zeo/solr.cfg
    _stage-settings.cfg
# Dev-Tools
    buildout.d/plone/test.cfg

develop =
    ${settings:develop}

# The [versions] pins below (zope.container, AccessControl, cffi, Pillow)
# are for packages whose C extensions don't compile on Apple Silicon -- see
# zope-buildout-apple-silicon-compile-fixes.md. The pin alone isn't the fix;
# install.sh pre-installs them into .venv (howto step 4).

[versions]
zope.container = 4.10
AccessControl = 5.7
RestrictedPython = 5.1
cffi = 1.17.1
Pillow = 8.3.0
python-magic = 0.4.27
EOFSTAGE
fi

if [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]
then
    echo ">> Step 4: pre-install Apple Silicon pins into .venv"
    ./.venv/bin/pip install --no-deps \
        "zope.container==4.10" "AccessControl==5.7" \
        "cffi==1.17.1" "Pillow==8.3.0"
else
    echo ">> Step 4: skipped (only needed on Apple Silicon macOS)"
fi

echo ">> Step 5: buildout (clones ~25 interaktiv.* repos on first run)"
./bin/buildout -c stage.cfg

echo ">> Done. Next: bin/instance fg, then see README.md 'After the install'."
