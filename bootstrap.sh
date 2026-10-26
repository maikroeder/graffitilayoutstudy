#!/usr/bin/env bash
# Howto step 2 (+ upstream checkout). Prepare a fresh Graffiti installation
# (Plone 5.2.2, Python 3.8):
#   1. Python venv with the pinned buildout
#   2. upstream/graffiti: Graffiti showcase project, branch main; its src/*
#      packages (graffiti.*, interaktiv.cronjob, interaktiv.workingcopy) are
#      symlinked into src/ so every develop path is a plain src/<name>
# The interaktiv.* tiles editor packages are checked out into src/ by
# mr.developer when bin/buildout runs (see buildout.d/base/sources.cfg).
set -e

PYTHON="${PYTHON:-python3.8}"
GRAFFITI_REPO="${GRAFFITI_REPO:-git@code.interaktiv.de:interaktiv/graffiti.git}"
GRAFFITI_REF="${GRAFFITI_REF:-main}"

if [ -d ".venv" ]
then
    echo ">> Removing existing Python venv.."
    rm -r .venv
fi
"$PYTHON" -m venv .venv || { echo "Couldn't create Python venv (python3.8 on PATH? try 'pyenv local 3.8.18')"; exit 1; }
./.venv/bin/pip install -r ./requirements.txt || { echo "Couldn't install required Python modules.."; exit 1; }
./.venv/bin/buildout bootstrap || { echo "Couldn't prepare buildout.."; exit 1; }
mkdir -p ./bin/ ./var/cache/

if [ ! -d "./upstream/graffiti/.git" ]
then
    mkdir -p ./upstream
    git clone --branch "$GRAFFITI_REF" "$GRAFFITI_REPO" ./upstream/graffiti
else
    echo ">> upstream/graffiti exists, leaving it untouched"
fi

for pkg in ./upstream/graffiti/src/*
do
    name="$(basename "$pkg")"
    ln -sfn "../upstream/graffiti/src/$name" "./src/$name"
done

echo ">> Ready: ./bin/buildout -c stage.cfg  (or ./install.sh for all steps)"
