import logging
import os

from graffiti.pdfcheck.checks import BUILTIN_CHECKS
from graffiti.pdfcheck.interfaces import IPdfCheck
from graffiti.pdfcheck.registry.pdfcheck import IPdfCheckSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtilitiesFor, queryUtility

logger = logging.getLogger('graffiti.pdfcheck')

PREFIX = 'graffiti.pdfcheck'
# the programs come from the environment of the server, never from the settings of the site: whoever may
# change the settings must not be able to start any program on the server
PROGRAM_VARIABLES = {'pdfunite': 'GRAFFITI_PDFCHECK_PDFUNITE', 'qpdf': 'GRAFFITI_PDFCHECK_QPDF'}
# the field with the file: File of Plone and other content types with a field of this name
FIELD = 'file'


def get_settings():
    """ The settings as a dict, None if the package is not installed in the current site """
    registry = queryUtility(IRegistry)
    if registry is None:
        return None
    try:
        proxy = registry.forInterface(IPdfCheckSettings, prefix=PREFIX)
    except KeyError:
        return None
    return {
        'enabled': bool(proxy.enabled),
        'portal_types': list(proxy.portal_types or []),
        'checks': [name.strip() for name in proxy.checks or [] if name and name.strip()],
        'timeout': proxy.timeout,
        'memory_mb': proxy.memory_mb,
        'max_size_mb': proxy.max_size_mb,
        'programs': get_programs(),
    }


def get_programs():
    """ The programs the checks call: a name on the PATH, or the full path from the environment variable """
    return {name: os.environ.get(variable) or name for name, variable in PROGRAM_VARIABLES.items()}


def available_checks():
    """ The built-in checks in the order they run, then the registered checks of projects by their name """
    builtin = {check.name for check in BUILTIN_CHECKS}
    registered = {}
    for name, check in getUtilitiesFor(IPdfCheck):
        if check.name in builtin:
            logger.warning('The check %s has the name of a built-in check and is left out', name)
            continue
        registered[check.name] = check
    return list(BUILTIN_CHECKS) + [registered[name] for name in sorted(registered)]


def get_checks(names):
    """ The checks for names of the settings, in the order they run.

    Names of checks that are not registered any more, for example of a removed package, are left out.
    """
    checks = [check for check in available_checks() if check.name in names]
    unknown = set(names) - {check.name for check in checks}
    if unknown:
        logger.warning('Unknown checks in the settings are left out: %s', ', '.join(sorted(unknown)))
    return checks
