""" Run a script like "bin/instance run" does, for a Python whose startup does not process the .pth files.

Usage (stop the instance first, it holds the database lock):
    .venv/bin/python -S parts/instance/bin/interpreter scripts/run_with_instance.py scripts/<script>.py [arguments]

Why: in this checkout .venv/lib/python3.8/site-packages has zope.container-*-nspkg.pth, which makes "zope" a namespace
that knows only the .venv folder, so "bin/instance run" cannot import zope.deferredimport from the eggs
("bin/instance fg" does not hit this). With "python -S" the .pth files are not processed and the eggs, which
the interpreter script puts on the path, extend the namespace themselves.

The script gets the same names as under "bin/instance run": "app" and sys.argv as if it was started directly.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(REPO, 'parts', 'instance', 'etc', 'zope.conf')

if len(sys.argv) < 2:
    raise SystemExit(__doc__)
TARGET = os.path.abspath(sys.argv[1])
sys.argv = [TARGET] + sys.argv[2:]

# The eggs now extend the namespace "zope" themselves, but not with the .venv folder, whose zope.container has no
# __init__.py (it relies on the .pth file that "-S" skips). Add that folder by hand.
import zope  # noqa: E402
VENV_ZOPE = os.path.join(REPO, '.venv', 'lib', 'python3.8', 'site-packages', 'zope')
if os.path.isdir(VENV_ZOPE) and VENV_ZOPE not in zope.__path__:
    zope.__path__.append(VENV_ZOPE)

import Zope2.Startup.run  # noqa: E402 - needs the paths of the interpreter script
Zope2.Startup.run.configure_wsgi(CONFIG)
import Zope2  # noqa: E402
app = Zope2.app()  # noqa: F841 - the target script uses it

with open(TARGET) as target_file:
    code = compile(target_file.read(), TARGET, 'exec')
exec(code, {'__name__': '__main__', '__file__': TARGET, 'app': app})
