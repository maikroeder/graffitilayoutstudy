#!/usr/bin/env bash
# Runs docs: ~/selfhosted/howtos/graffiti-plone-buildout-fresh-install.md, steps 0 and 2-5, in order.
set -e

echo ">> Step 0: prerequisites"
command -v "${PYTHON:-python3.8}" >/dev/null || { echo "python3.8 not on PATH (pyenv local 3.8.18?)"; exit 1; }
command -v node >/dev/null && command -v npm >/dev/null || { echo "node/npm required (update_styleguide part)"; exit 1; }
ssh -o BatchMode=yes -T git@code.interaktiv.de || { echo "SSH access to code.interaktiv.de failed"; exit 1; }

echo ">> Step 2: bootstrap venv + buildout + upstream checkout"
./bootstrap.sh

echo ">> Step 3: stage.cfg"
[ -f stage.cfg ] || { echo "stage.cfg missing (gitignored); restore it from the howto step 3"; exit 1; }

if [ "$(uname -s)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]
then
    echo ">> Step 4: pre-install Apple Silicon pins into .venv"
    ./.venv/bin/pip install --no-deps \
        "zope.container==4.10" "AccessControl==5.7" \
        "cffi==1.17.1" "Pillow==8.3.0"
fi

echo ">> Step 5: buildout (clones ~25 interaktiv.* repos on first run)"
./bin/buildout -c stage.cfg

echo ">> Done. Start with: bin/instance fg  (http://localhost:8080/manage -> add a Plone site)"
