#!/usr/bin/env bash
# Howto step 2. Prepare a fresh Graffiti installation (Plone 5.2.2, Python 3.8):
# Python venv with the pinned buildout. The Graffiti packages (graffiti.*,
# interaktiv.cronjob, interaktiv.workingcopy) are vendored in src/; the
# interaktiv.* tiles editor packages are checked out into src/ by mr.developer
# when bin/buildout runs (see buildout.d/base/sources.cfg).
set -e

PYTHON="${PYTHON:-python3.8}"

if [ -d ".venv" ]
then
    echo ">> Removing existing Python venv.."
    rm -r .venv
fi
"$PYTHON" -m venv .venv || { echo "Couldn't create Python venv (python3.8 on PATH? try 'pyenv local 3.8.18')"; exit 1; }
./.venv/bin/pip install -r ./requirements.txt || { echo "Couldn't install required Python modules.."; exit 1; }
./.venv/bin/buildout bootstrap || { echo "Couldn't prepare buildout.."; exit 1; }
mkdir -p ./bin/ ./var/cache/

echo ">> Ready: ./bin/buildout -c stage.cfg  (or ./install.sh for all steps)"
