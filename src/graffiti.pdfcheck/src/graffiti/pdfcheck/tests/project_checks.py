""" Checks the way a project adds them, for the tests: runs in the process of the checks, so no Zope here. """
import os
import subprocess

from graffiti.pdfcheck.checks import Check, finding, ok, skipped

# the test writes the process id of the slow check here, to see that the time limit stops it
PID_FILE = 'GRAFFITI_PDFCHECK_TEST_PID_FILE'


def check_one_page(context):
    """ An example of an own check: the project allows only one page """
    if context.reader() is None:
        return skipped('skipped, pypdf could not open the file')
    if context.pages > 1:
        return finding('too_many_pages', '%d pages, allowed is 1' % context.pages)
    return ok('1 page')


def check_broken(context):
    return 1 / 0


def check_slow(context):
    """ Waits for a program that runs longer than the time limit of the test """
    process = subprocess.Popen(['sleep', '60'])
    if os.environ.get(PID_FILE):
        with open(os.environ[PID_FILE], 'w') as pid_file:
            pid_file.write(str(process.pid))
    process.wait()
    return ok('done')


def check_greedy(context):
    """ Needs more memory than the limit of the test allows """
    data = bytearray(2 * 1024 * 1024 * 1024)
    return ok('%d bytes' % len(data))


def check_crash(context):
    os.abort()


def check_noisy(context):
    """ Writes to stdout like a careless check, without a line break """
    print('some output of a check', end='', flush=True)
    return ok('done')


def check_reads_input(context):
    """ Would wait for the terminal of Zope if the check process had its input """
    import sys
    return ok('read %d characters' % len(sys.stdin.read()))


def check_detached(context):
    """ Starts a program in a session of its own that keeps the output open, then waits for the time limit """
    process = subprocess.Popen(['setsid', 'sleep', '30'])
    if os.environ.get(PID_FILE):
        with open(os.environ[PID_FILE], 'w') as pid_file:
            pid_file.write(str(process.pid))
    subprocess.call(['sleep', '60'])


ONE_PAGE = Check('one_page', 'pypdf', 'too_many_pages', check_one_page, 'Only one page per file',
                 {'too_many_pages': 'The file may only have one page.'})
BROKEN = Check('broken', 'script', 'broken', check_broken)
SLOW = Check('slow', 'sleep', 'slow', check_slow)
GREEDY = Check('greedy', 'script', 'greedy', check_greedy)
CRASH = Check('crash', 'script', 'crash', check_crash)
NOISY = Check('noisy', 'script', 'noisy', check_noisy)
READS_INPUT = Check('reads_input', 'script', 'reads_input', check_reads_input)
DETACHED = Check('detached', 'sleep', 'detached', check_detached)
