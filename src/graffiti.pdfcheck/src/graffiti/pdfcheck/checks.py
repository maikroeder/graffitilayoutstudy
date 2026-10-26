""" The checks for one PDF file, in plain Python without Zope.

The runner starts this module in its own process:

    python -m graffiti.pdfcheck.checks FILE [--checks open,text] [--check CHECK] [--memory-mb 1024]
        [--program qpdf=/opt/qpdf/bin/qpdf]

It prints the result as JSON on stdout. Only the standard library and pypdf are imported, so the process starts fast.
"""
import argparse
import collections
import datetime
import importlib
import io
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

# findings make a file unsuitable: the short codes and a text for people
FINDINGS = {
    'damaged': 'damaged, can not be opened',
    'crypto_missing': 'encrypted with AES, the Python package cryptography is missing for the check',
    'password': 'encrypted, a password is needed to open it',
    'edit_protection': 'edit protection (encrypted, but opens without a password)',
    'no_text': 'no text can be read, for example a scan',
    'rewrite': 'can not be rebuilt page by page and get metadata',
    'pdfunite': 'pdfunite can not append a second PDF',
    'qpdf': 'qpdf finds errors in the file',
    'timeout': 'time limit exceeded',
    'memory': 'memory limit exceeded',
    'check_error': 'the check could not run',
}
# hints tell editors something, but do not change whether a file is suitable
HINTS = {
    'qpdf_warnings': 'qpdf finds problems that it can repair',
    'lost_outlines': 'bookmarks are lost',
    'lost_form_fields': 'form fields are lost',
    'lost_signatures': 'signatures are lost',
    'lost_embedded_files': 'embedded files are lost',
    'not_checked': 'not checked',
}

# a check: its name, the tool it uses, the finding when it fails with an error, the function;
# for checks of projects (the built-in checks have translated texts in graffiti.pdfcheck.messages):
# the title on the settings page, and a sentence for editors per code of a finding or hint
Check = collections.namedtuple('Check', 'name tool finding function title texts', defaults=(None, None))

# the programs the checks call: a name on the PATH or a full path
PROGRAMS = {'pdfunite': 'pdfunite', 'qpdf': 'qpdf'}
# fewer characters in the whole file count as "no text", spaces and line breaks do not count
MIN_CHARACTERS = 1
# what a later processing may lose: key, hint, singular, plural
FEATURES = [
    ('outlines', 'lost_outlines', 'bookmark', 'bookmarks'),
    ('form_fields', 'lost_form_fields', 'form field', 'form fields'),
    ('signatures', 'lost_signatures', 'signature', 'signatures'),
    ('embedded_files', 'lost_embedded_files', 'embedded file', 'embedded files'),
]
NOT_OPENED = 'skipped, pypdf could not open the file'
# for the runner, the lines with a result start with this, so that other output of a check can not be mistaken for it
RESULT_MARKER = 'graffiti.pdfcheck result: '


def ok(text, hints=None):
    return {'state': 'hint' if hints else 'ok', 'text': text, 'finding': None, 'hints': list(hints or [])}


def finding(code, text=None):
    return {'state': 'finding', 'text': text or FINDINGS.get(code, code), 'finding': code, 'hints': []}


def skipped(text, hints=None):
    return {'state': 'skipped', 'text': text, 'finding': None, 'hints': list(hints or [])}


def short(error):
    message = str(error).splitlines()[0][:100] if str(error) else ''
    return '%s: %s' % (type(error).__name__, message)


def pages_text(count):
    return '%d %s' % (count, 'page' if count == 1 else 'pages')


class Context(object):
    """ What the checks of one file share: the path, the programs and the file opened with pypdf. """

    def __init__(self, path, programs=None):
        self.path = path
        self.programs = dict(PROGRAMS, **(programs or {}))
        self.versions = {}
        self.pages = None
        self.encrypted = False
        self.password_needed = False
        self.open_error = None
        self._reader = None
        self._opened = False
        self._features = None

    def reader(self):
        """ The file opened with pypdf, None if pypdf can not open it. Opens the file only once. """
        if not self._opened:
            self._opened = True
            from pypdf import PdfReader
            try:
                reader = PdfReader(self.path, strict=False)
                if reader.is_encrypted:
                    self.encrypted = True
                    # a file with only an owner password opens with an empty user password
                    if not reader.decrypt(''):
                        self.password_needed = True
                        return None
                self.pages = len(reader.pages)
                self._reader = reader
            except MemoryError:
                raise
            except Exception as error:  # noqa: every error of pypdf means the file can not be processed
                self.open_error = error
        return self._reader

    def features(self):
        """ The bookmarks, form fields, signatures and embedded files of the file, see `count_features` """
        if self._features is None and self.reader() is not None:
            self._features = count_features(self.reader())
        return self._features

    def program(self, name):
        """ The full path of a program, None if it is not installed. Records its version. """
        command = shutil.which(self.programs.get(name, name))
        if command and name not in self.versions:
            self.versions[name] = program_version(command, name)
        return command


def program_version(command, name):
    option = '-v' if name == 'pdfunite' else '--version'
    try:
        output = subprocess.run([command, option], capture_output=True, stdin=subprocess.DEVNULL, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    found = re.search(r'\d+(\.\d+)+', (output.stdout + output.stderr).decode('utf-8', 'replace'))
    return found.group(0) if found else None


def is_pdf(path):
    """ The PDF header may come after some bytes, as long as it is in the first 1024 bytes """
    with open(path, 'rb') as pdf_file:
        return b'%PDF-' in pdf_file.read(1024)


def counted(function, *arguments):
    """ The number that the function counts, None if the structure of the file does not allow it """
    try:
        return function(*arguments)
    except MemoryError:
        raise
    except Exception:  # noqa: a broken part of the file can not be counted
        return None


def count_outline(items):
    return sum(count_outline(item) if isinstance(item, list) else 1 for item in items)


def count_names(node):
    """ The entries of a name tree, for example of the embedded files """
    node = node.get_object()
    return len(node.get('/Names', [])) // 2 + sum(count_names(kid) for kid in node.get('/Kids', []))


def count_embedded_files(reader):
    names = reader.trailer['/Root'].get_object().get('/Names')
    if names is None or '/EmbeddedFiles' not in names.get_object():
        return 0
    return count_names(names.get_object()['/EmbeddedFiles'])


def count_fields(reader, signatures):
    """ Form fields without signatures, or signature fields with a value """
    fields = (reader.get_fields() or {}).values()
    if signatures:
        return sum(1 for field in fields if field.get('/FT') == '/Sig' and field.get('/V') is not None)
    return sum(1 for field in fields if field.get('/FT') not in (None, '/Sig'))


def count_features(reader):
    return {
        'outlines': counted(lambda: count_outline(reader.outline)),
        'form_fields': counted(count_fields, reader, False),
        'signatures': counted(count_fields, reader, True),
        'embedded_files': counted(count_embedded_files, reader),
    }


def lost_features(before, after):
    """ The hints for what the original file has and the result has less of, and a text about it """
    hints = []
    texts = []
    for key, hint, singular, plural in FEATURES:
        old, new = before.get(key), after.get(key)
        if old and new is not None and new < old:
            hints.append(hint)
            texts.append('%d of %d %s' % (old - new, old, singular if old == 1 else plural))
    return hints, ('; lost: ' + ', '.join(texts)) if texts else ''


def check_open(context):
    context.reader()
    if context.open_error is not None:
        if is_crypto_missing(context.open_error):
            return finding('crypto_missing')
        return finding('damaged', 'damaged: ' + short(context.open_error))
    if context.password_needed:
        return finding('password')
    if context.encrypted:
        return finding('edit_protection', '%s, %s' % (FINDINGS['edit_protection'], pages_text(context.pages)))
    return ok(pages_text(context.pages))


def check_text(context):
    reader = context.reader()
    if reader is None:
        return skipped(NOT_OPENED)
    characters = sum(len((page.extract_text() or '').strip()) for page in reader.pages)
    if characters >= MIN_CHARACTERS:
        return ok('%d characters' % characters)
    return finding('no_text', 'no text found (%d characters), for example a scan' % characters)


def check_rewrite(context):
    """ Rebuild the file page by page, add metadata and read the result again """
    reader = context.reader()
    if reader is None:
        return skipped(NOT_OPENED)
    from pypdf import PdfReader, PdfWriter
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({'/Title': 'Check', '/Subject': 'Check of the processing'})
    buffer = io.BytesIO()
    writer.write(buffer)
    rebuilt = PdfReader(io.BytesIO(buffer.getvalue()))
    if len(rebuilt.pages) != context.pages:
        return finding('rewrite', 'pages lost: %d of %d' % (len(rebuilt.pages), context.pages))
    if rebuilt.metadata is None or rebuilt.metadata.title != 'Check':
        return finding('rewrite', 'metadata lost')
    hints, lost = lost_features(context.features(), count_features(rebuilt))
    return ok('pages and metadata complete' + lost, hints)


def check_pdfunite(context):
    """ Append a blank page with pdfunite. Runs also when pypdf fails: both tools fail on different files. """
    command = context.program('pdfunite')
    if not command:
        # not a finding: the system can not do this check
        return skipped('skipped, pdfunite is not installed')
    from pypdf import PdfReader, PdfWriter
    with tempfile.TemporaryDirectory(prefix='pdfcheck-') as folder:
        blank = os.path.join(folder, 'blank.pdf')
        writer = PdfWriter()
        writer.add_blank_page(width=595, height=842)
        with open(blank, 'wb') as blank_file:
            writer.write(blank_file)
        target = os.path.join(folder, 'united.pdf')
        united = subprocess.run([command, context.path, blank, target], capture_output=True, stdin=subprocess.DEVNULL)
        if united.returncode != 0 or not os.path.exists(target):
            message = first_line(united.stderr, context.path)
            return finding('pdfunite', message or 'exit code %d' % united.returncode)
        if context.reader() is None:
            return ok('appended')
        # pdfunite may leave out pages and still end without an error
        result = PdfReader(target)
        if len(result.pages) != context.pages + 1:
            return finding('pdfunite', 'pages lost: %d instead of %d pages after appending one page' % (
                len(result.pages), context.pages + 1))
        hints, lost = lost_features(context.features(), count_features(result))
    return ok('appended' + lost, hints)


def check_qpdf(context):
    """ qpdf reads the whole structure of the file. Warnings are problems that qpdf can repair. """
    command = context.program('qpdf')
    if not command:
        return skipped('skipped, qpdf is not installed')
    checked = subprocess.run([command, '--check', context.path], capture_output=True, stdin=subprocess.DEVNULL)
    message = first_line(checked.stderr + checked.stdout, context.path, ('WARNING', 'qpdf:', 'ERROR'))
    if checked.returncode == 0:
        return ok('no problems found')
    if checked.returncode == 3:
        return ok(message or 'warnings', ['qpdf_warnings'])
    return finding('qpdf', message or 'exit code %d' % checked.returncode)


def first_line(output, path, prefixes=None):
    """ The first message of a program, with the name of the file instead of its full path """
    for line in output.decode('utf-8', 'replace').splitlines():
        line = line.strip()
        if line and (prefixes is None or line.startswith(prefixes)):
            return line.replace(path, os.path.basename(path))[:120]
    return ''


def is_crypto_missing(error):
    """ AES needs an additional package: not a damaged file, but an incomplete check """
    return type(error).__name__ == 'DependencyError'


BUILTIN_CHECKS = [
    Check('open', 'pypdf', 'damaged', check_open),
    Check('text', 'pypdf', 'no_text', check_text),
    Check('rewrite', 'pypdf', 'rewrite', check_rewrite),
    Check('pdfunite', 'pdfunite', 'pdfunite', check_pdfunite),
    Check('qpdf', 'qpdf', 'qpdf', check_qpdf),
]


def is_builtin(check):
    return any(check is builtin for builtin in BUILTIN_CHECKS)


def function_name(check):
    """ The dotted name of the function of a check """
    return '%s.%s' % (check.function.__module__, check.function.__qualname__)


def check_spec(check):
    """ A check of a project as a dict, so that the check process can import it: its function by its dotted name """
    module, function = check.function.__module__, check.function.__qualname__
    if '<' in function:
        raise ValueError('The function of the check %s must be defined at the top level of its module' % check.name)
    return {'name': check.name, 'tool': check.tool, 'finding': check.finding, 'module': module, 'function': function}


def check_from_spec(spec):
    function = importlib.import_module(spec['module'])
    for part in spec['function'].split('.'):
        function = getattr(function, part)
    return Check(spec['name'], spec['tool'], spec['finding'], function)


def resolve_checks(checks=None):
    """ The checks for a list: Check objects, names of built-in checks, the dotted name of a Check of a project,
    or a check as a dict of `check_spec`. None returns the built-in checks. """
    if checks is None:
        return list(BUILTIN_CHECKS)
    builtin = {check.name: check for check in BUILTIN_CHECKS}
    resolved = []
    for item in checks:
        if isinstance(item, Check):
            resolved.append(item)
        elif isinstance(item, dict):
            resolved.append(check_from_spec(item))
        elif item in builtin:
            resolved.append(builtin[item])
        else:
            module_name, _, attribute = item.rpartition('.')
            if not module_name:
                raise ValueError('Unknown check: %s' % item)
            check = getattr(importlib.import_module(module_name), attribute, None)
            if not (hasattr(check, 'name') and callable(getattr(check, 'function', None))):
                raise ValueError('Not a check: %s' % item)
            resolved.append(check)
    return resolved


def run_check(check, context):
    try:
        return check.function(context)
    except MemoryError:
        return finding('memory', 'needed more memory than allowed')
    except Exception as error:  # noqa: an error of a tool is a finding of the check
        if is_crypto_missing(error):
            return finding('crypto_missing')
        return finding(check.finding, short(error))


def pypdf_version():
    try:
        import pypdf
        return pypdf.__version__
    except ImportError:
        return None


def new_result():
    return {
        'is_pdf': None,
        'suitable': None,
        'findings': [],
        'hints': [],
        'steps': {},
        'pages': None,
        'versions': {'python': platform.python_version(), 'pypdf': pypdf_version()},
        'checked_at': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        'seconds': None,
    }


def add_step(result, name, tool, step):
    step = dict(step, tool=tool)
    result['steps'][name] = step
    if step['finding'] and step['finding'] not in result['findings']:
        result['findings'].append(step['finding'])
    for hint in step.get('hints') or []:
        if hint not in result['hints']:
            result['hints'].append(hint)


def finish(result):
    """ Suitable: True, False, or None for files that are no PDF or were not checked """
    checked = any(step['state'] in ('ok', 'hint') for name, step in result['steps'].items() if name != 'header')
    if result['is_pdf'] and not result['findings'] and not checked and 'not_checked' not in result['hints']:
        # no check could run, for example the programs are missing, or pypdf can not open the file and the check
        # "open" is switched off: that is no suitable file
        result['hints'].append('not_checked')
    if result['is_pdf'] is False:
        result['suitable'] = None
    elif result['findings']:
        result['suitable'] = False
    else:
        result['suitable'] = None if 'not_checked' in result['hints'] else True
    return result


def run_checks(path, checks=None, progress=None, programs=None):
    """ Runs the checks for one file and returns the result as a dict.

    `checks` is a list of checks or their names (see `resolve_checks`), None runs all built-in checks.
    `progress` is called with the result so far and the name of the next check.
    `programs` changes the paths of programs, for example `{'qpdf': '/opt/qpdf/bin/qpdf'}`.
    """
    start = time.time()
    result = new_result()
    result['is_pdf'] = is_pdf(path)
    if not result['is_pdf']:
        add_step(result, 'header', 'script', skipped('missing, the file does not start with %PDF-, no further checks'))
    else:
        add_step(result, 'header', 'script', ok('found'))
        context = Context(path, programs)
        for check in resolve_checks(checks):
            if progress:
                progress(result, check.name)
            add_step(result, check.name, check.tool, run_check(check, context))
            if context.pages is not None:
                result['pages'] = context.pages
            result['versions'].update(context.versions)
    result['seconds'] = round(time.time() - start, 2)
    return finish(result)


def limit_memory(memory_mb):
    try:
        import resource
        limit = memory_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except (ImportError, ValueError, OSError):
        # not every system knows this limit, then only the time limit applies
        pass


def print_json(data, marker=''):
    print(marker + json.dumps(data), flush=True)


def main(arguments=None):
    parser = argparse.ArgumentParser(description='Checks whether a PDF file can be processed later.')
    parser.add_argument('path', help='the file to check')
    parser.add_argument('--checks', help='names of the checks, separated by commas: built-in checks or the dotted '
                                         'name of a check of a project (default: all built-in checks)')
    parser.add_argument('--check', action='append', default=[],
                        help='one check: a name as in --checks, or a check of a project as JSON, for the runner; '
                             'runs after the checks of --checks')
    parser.add_argument('--memory-mb', type=int, help='memory limit of this process in megabytes')
    parser.add_argument('--program', action='append', default=[], metavar='NAME=PATH',
                        help='path of a program, for example qpdf=/opt/qpdf/bin/qpdf')
    parser.add_argument('--progress', action='store_true',
                        help='print the result so far before each check, for the runner')
    arguments = parser.parse_args(arguments)
    # pypdf writes a warning for every problem of a broken file
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    checks = (arguments.checks.split(',') if arguments.checks else []) + [
        json.loads(check) if check.startswith('{') else check for check in arguments.check]
    programs = dict(program.split('=', 1) for program in arguments.program)
    if arguments.memory_mb:
        limit_memory(arguments.memory_mb)

    # the runner reads only the marked lines, people get plain JSON
    marker = RESULT_MARKER if arguments.progress else ''

    def progress(result, name):
        print_json(dict(result, running=name), marker)

    print_json(run_checks(os.path.abspath(arguments.path), checks or None, progress if arguments.progress else None,
                          programs), marker)


if __name__ == '__main__':
    # run main() of the imported module, so that checks of projects share its Check and helpers
    from graffiti.pdfcheck.checks import main as imported_main
    sys.exit(imported_main())
