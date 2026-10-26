from graffiti.pdfcheck.interfaces import IPdfCheckRunner
from graffiti.pdfcheck.runner import check_pdf
from graffiti.pdfcheck.settings import get_checks
from zope.interface import implementer


@implementer(IPdfCheckRunner)
class LocalRunner(object):
    """ Runs the checks on this host, in their own process """

    def check(self, path, settings):
        return check_pdf(
            path,
            timeout=settings['timeout'],
            memory_mb=settings['memory_mb'],
            # no checks in the settings: the built-in checks
            checks=get_checks(settings['checks']) or None,
            max_size_mb=settings['max_size_mb'],
            programs=settings['programs'],
        )
