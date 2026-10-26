""" Runs the checks of `graffiti.pdfcheck.checks` in its own process with a time and a memory limit.

A crafted or very large file can then not block or crash the caller. The process gets the import path of the caller,
so it finds pypdf and the checks of projects also when they come from buildout eggs.
"""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time

from graffiti.pdfcheck.checks import (
    RESULT_MARKER, add_step, check_spec, finding, finish, is_builtin, is_pdf, new_result, ok, resolve_checks,
    run_checks, skipped
)

# default limits per file: the check runs while the editor waits for the upload
TIMEOUT = 30
MEMORY_MB = 1024
MAX_SIZE_MB = 50
# after the time limit, how long to wait for the output of the stopped process
WAIT_AFTER_KILL = 5
# the Python of the check process, for servers where sys.executable is no Python (mod_wsgi, uWSGI)
PYTHON_VARIABLE = 'GRAFFITI_PDFCHECK_PYTHON'


def check_pdf(data_or_path, timeout=TIMEOUT, memory_mb=MEMORY_MB, checks=None, max_size_mb=MAX_SIZE_MB,
              programs=None):
    """ Checks one file and returns the result of `graffiti.pdfcheck.checks.run_checks` as a dict.

    `data_or_path` is the content of the file as bytes or the path of the file.
    `timeout` is in seconds, `memory_mb` in megabytes. Exceeding a limit is the finding `timeout` or `memory`.
    `checks` is a list of checks or their names (see `graffiti.pdfcheck.checks.resolve_checks`), None runs all
    built-in checks.
    Larger files than `max_size_mb` are not checked: the hint `not_checked`, suitable is None. None checks every file.
    `programs` changes the paths of programs, for example `{'qpdf': '/opt/qpdf/bin/qpdf'}`.
    """
    # unknown names fail here and not as a finding of every file
    resolved = resolve_checks(checks)
    # built-in checks by their name, checks of projects with the dotted name of their function
    check_arguments = [] if checks is None else [
        argument for check in resolved
        for argument in ('--check', check.name if is_builtin(check) else json.dumps(check_spec(check)))]
    start = time.time()
    with tempfile.TemporaryDirectory(prefix='pdfcheck-') as folder:
        if isinstance(data_or_path, (bytes, bytearray)):
            path = os.path.join(folder, 'file.pdf')
            with open(path, 'wb') as pdf_file:
                pdf_file.write(data_or_path)
        else:
            path = os.path.abspath(os.fspath(data_or_path))
        if not is_pdf(path):
            # files that are no PDF stay untouched, no process needed
            return run_checks(path, resolved)
        size = os.path.getsize(path)
        if max_size_mb is not None and size > max_size_mb * 1024 * 1024:
            return too_large(size, max_size_mb)
        python = os.environ.get(PYTHON_VARIABLE) or sys.executable
        command = [python, '-m', 'graffiti.pdfcheck.checks', path, '--progress', '--memory-mb', str(memory_mb)]
        command += check_arguments
        for name, program in sorted((programs or {}).items()):
            command += ['--program', '%s=%s' % (name, program)]
        # its own working folder, so that no module of the current folder is imported by mistake;
        # its own session, so that a timeout also stops pdfunite
        # no input: a program that reads it would otherwise wait for the terminal of Zope
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   cwd=folder, env=child_environment(), start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                stdout, stderr = process.communicate(timeout=WAIT_AFTER_KILL)
            except subprocess.TimeoutExpired:
                # a program that left the session keeps the output open: do not wait for it
                for pipe in (process.stdout, process.stderr):
                    pipe.close()
                process.wait()
                stdout, stderr = b'', b''
    result = last_result(stdout)
    if result is None or 'running' in result:
        result = stopped_result(result, resolved, stderr, process.returncode, timed_out, timeout, memory_mb)
    result['seconds'] = round(time.time() - start, 2)
    return result


def too_large(size, max_size_mb):
    result = new_result()
    result['is_pdf'] = True
    add_step(result, 'header', 'script', ok('found'))
    text = 'not checked, the file has %.1f MB, the limit is %d MB' % (size / 1024.0 / 1024.0, max_size_mb)
    add_step(result, 'size', 'script', skipped(text, ['not_checked']))
    result['seconds'] = 0.0
    return finish(result)


def child_environment():
    environment = dict(os.environ)
    paths = [os.path.abspath(path) for path in sys.path if path]
    environment['PYTHONPATH'] = os.pathsep.join(paths)
    return environment


def last_result(stdout):
    """ The last marked line on stdout: the final result, or the result so far if the process was stopped.
    Other output, for example of a check of a project, is left out. """
    for line in reversed(stdout.decode('utf-8', 'replace').splitlines()):
        # output of a check without a line break ends up in front of the marker
        position = line.rfind(RESULT_MARKER)
        if position < 0:
            continue
        try:
            result = json.loads(line[position + len(RESULT_MARKER):])
        except ValueError:
            continue
        if isinstance(result, dict) and 'steps' in result and 'findings' in result:
            return result
    return None


def stopped_result(result, checks, stderr, returncode, timed_out, timeout, memory_mb):
    """ The process did not finish: the check that was running gets the finding """
    if result is None:
        result = new_result()
        result['is_pdf'] = True
    running = result.pop('running', None)
    error = stderr.decode('utf-8', 'replace').strip()
    if timed_out:
        step = finding('timeout', 'stopped after %s seconds' % timeout)
    elif 'MemoryError' in error:
        step = finding('memory', 'needed more than %d MB of memory, stopped' % memory_mb)
    else:
        lines = error.splitlines()
        # a crash of Python names itself in this line, an exception in the last line
        fatal = [line for line in lines if line.startswith('Fatal Python error')]
        message = (fatal[:1] or lines[-1:] or ['without a message'])[0][:100]
        text = 'the check process stopped (exit code %s): %s' % (returncode, message)
        codes = {check.name: check.finding for check in checks}
        if running is None:
            # stopped before the first check, for example a wrong Python: a problem of the server, not of the file
            step = skipped('not checked, %s' % text, ['not_checked'])
        else:
            # a crash in a check means that this step would fail in the later processing as well
            step = finding(codes.get(running, 'check_error'), text)
    tools = {check.name: check.tool for check in checks}
    add_step(result, running or 'runner', tools.get(running, 'runner'), step)
    for check in checks:
        if check.name not in result['steps']:
            add_step(result, check.name, check.tool, skipped('skipped, the check process stopped before'))
    return finish(result)
