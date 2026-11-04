""" Apply the theme openheidelberg.layout again, so that Plone takes over the current manifest.cfg.

Usage:
    scripts/run_with_instance.py (see there) scripts/apply_theme.py [site_id]

Plone copies the rules, the parameters and the doctype of a theme into its registry when the theme is applied
(plone.app.theming.utils.applyTheme). A change in manifest.cfg, for instance of the theme parameter
site_layout_enabled, reaches the running site only after that; a restart of the server is not enough.
Running it twice gives the same result.
"""
import os
import sys

from plone.app.theming.utils import applyTheme
from plone.app.theming.utils import getTheme

THEME_ID = 'openheidelberg.layout'

# "bin/instance run" puts its own options in front of the script name, the arguments follow it
SCRIPT_ARGS = []
for arg in sys.argv[1:]:
    if not arg.startswith('-'):
        SCRIPT_ARGS.append(arg)
last_script = 0
for index in range(len(SCRIPT_ARGS)):
    if SCRIPT_ARGS[index].endswith('.py'):
        last_script = index
SCRIPT_ARGS = SCRIPT_ARGS[last_script + 1:]
SITE_ID = SCRIPT_ARGS[0] if SCRIPT_ARGS else 'Plone'

SCRIPT_PATH = [arg for arg in sys.argv if arg.endswith('.py')][-1]
sys.path.insert(0, os.path.dirname(os.path.abspath(SCRIPT_PATH)))
import demo_common  # noqa: E402 - needs the folder of the scripts on the path

portal = demo_common.setup_site(app, SITE_ID)  # noqa: F821 - provided by "bin/instance run"

theme = getTheme(THEME_ID)
if theme is None:
    raise SystemExit('theme not found: ' + THEME_ID)
print('parameters before:', dict(theme.parameterExpressions))
applyTheme(theme)
print('theme applied:', THEME_ID)
demo_common.commit()
