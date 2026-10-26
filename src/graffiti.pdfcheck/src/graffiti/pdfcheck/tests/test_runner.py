""" Tests of the checks in their own process: limits, crashes, bytes and paths. Runs without Plone. """
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from graffiti.pdfcheck import runner
from graffiti.pdfcheck.checks import Check, ok
from graffiti.pdfcheck.tests import project_checks, samples

PROJECT = 'graffiti.pdfcheck.tests.project_checks.'
HAS_PDFUNITE = shutil.which('pdfunite') is not None
# pypdf makes Python 3.8 crash on deeply nested objects, later versions of Python raise an error
PYTHON_CRASHES = sys.version_info < (3, 9)


def is_running(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class TestRunner(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='pdfcheck-test-')
        self.addCleanup(shutil.rmtree, self.folder)

    @unittest.skipUnless(HAS_PDFUNITE, 'pdfunite is not installed')
    def test_bytes(self):
        result = runner.check_pdf(samples.good())
        self.assertIs(result['suitable'], True)
        self.assertEqual(list(result['steps']), ['header', 'open', 'text', 'rewrite', 'pdfunite', 'qpdf'])
        self.assertEqual(result['pages'], 2)

    def test_path(self):
        result = runner.check_pdf(samples.write('edit_protection', self.folder), checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['edit_protection'])

    def test_not_pdf_needs_no_process(self):
        result = runner.check_pdf(samples.not_pdf())
        self.assertIsNone(result['suitable'])
        self.assertEqual(result['findings'], [])

    def test_time_limit(self):
        pid_file = os.path.join(self.folder, 'pid')
        os.environ[project_checks.PID_FILE] = pid_file
        self.addCleanup(os.environ.pop, project_checks.PID_FILE)
        result = runner.check_pdf(samples.good(), timeout=2, checks=['open', PROJECT + 'SLOW'])
        self.assertEqual(result['findings'], ['timeout'])
        self.assertIs(result['suitable'], False)
        # the checks before the time limit keep their result
        self.assertEqual(result['steps']['open']['state'], 'ok')
        self.assertEqual(result['steps']['slow']['text'], 'stopped after 2 seconds')
        self.assertLess(result['seconds'], 10)
        # the program started by the check is stopped as well
        with open(pid_file) as pid_file:
            pid = int(pid_file.read())
        for _ in range(20):
            if not is_running(pid):
                break
            time.sleep(0.1)
        self.assertFalse(is_running(pid))

    def test_check_of_a_project_as_object(self):
        """ Registered checks reach the runner as objects, the check process imports their function """
        result = runner.check_pdf(samples.good(), checks=['open', project_checks.ONE_PAGE])
        self.assertEqual(list(result['steps']), ['header', 'open', 'one_page'])
        self.assertEqual(result['findings'], ['too_many_pages'])

    def test_check_with_a_function_that_can_not_be_imported(self):
        local = Check('local', 'script', 'local', lambda context: ok('done'))
        with self.assertRaises(ValueError):
            runner.check_pdf(samples.good(), checks=[local])

    def test_memory_limit(self):
        result = runner.check_pdf(samples.good(), memory_mb=256, checks=['open', PROJECT + 'GREEDY'])
        self.assertEqual(result['findings'], ['memory'])
        self.assertEqual(result['steps']['open']['state'], 'ok')

    def test_output_of_a_check_is_no_result(self):
        result = runner.check_pdf(samples.good(), checks=['open', project_checks.NOISY])
        self.assertIs(result['suitable'], True)
        self.assertEqual(result['steps']['noisy']['text'], 'done')

    def test_check_process_has_no_input(self):
        result = runner.check_pdf(samples.good(), timeout=10, checks=[project_checks.READS_INPUT])
        self.assertEqual(result['steps']['reads_input']['text'], 'read 0 characters')

    def test_program_that_keeps_the_output_open(self):
        """ After the time limit the runner waits a few seconds for the output, not for the program """
        pid_file = os.path.join(self.folder, 'pid')
        os.environ[project_checks.PID_FILE] = pid_file
        self.addCleanup(os.environ.pop, project_checks.PID_FILE)
        result = runner.check_pdf(samples.good(), timeout=2, checks=[project_checks.DETACHED])
        with open(pid_file) as pid_file:
            os.kill(int(pid_file.read()), 9)
        self.assertEqual(result['findings'], ['timeout'])
        self.assertLess(result['seconds'], 2 + runner.WAIT_AFTER_KILL + 3)

    def test_stop_before_the_first_check_is_no_finding(self):
        """ For example a wrong Python on the server: the file is not checked, it is not unsuitable """
        os.environ[runner.PYTHON_VARIABLE] = shutil.which('false')
        self.addCleanup(os.environ.pop, runner.PYTHON_VARIABLE)
        result = runner.check_pdf(samples.good())
        self.assertEqual(result['findings'], [])
        self.assertIn('not_checked', result['hints'])
        self.assertIsNone(result['suitable'])

    def test_crash_is_finding_of_the_running_check(self):
        result = runner.check_pdf(samples.good(), checks=['open', PROJECT + 'CRASH'])
        self.assertEqual(result['findings'], ['crash'])
        self.assertIn('the check process stopped', result['steps']['crash']['text'])

    def test_crash_skips_the_other_checks(self):
        result = runner.check_pdf(samples.good(), checks=['open', PROJECT + 'CRASH', 'text'])
        self.assertEqual(result['steps']['text']['state'], 'skipped')
        self.assertEqual(list(result['steps']), ['header', 'open', 'crash', 'text'])

    @unittest.skipUnless(PYTHON_CRASHES, 'Python does not crash on deeply nested objects')
    def test_python_crash(self):
        result = runner.check_pdf(samples.nested(), checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['rewrite'])
        self.assertIn('Fatal Python error', result['steps']['rewrite']['text'])

    @unittest.skipIf(PYTHON_CRASHES, 'Python crashes on deeply nested objects')
    def test_deeply_nested_object(self):
        result = runner.check_pdf(samples.nested(), checks=['open', 'text', 'rewrite'])
        self.assertIs(result['suitable'], True)

    def test_too_large_file_is_not_checked(self):
        result = runner.check_pdf(samples.damaged(), max_size_mb=0)
        self.assertIsNone(result['suitable'])
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['hints'], ['not_checked'])
        self.assertIn('the limit is 0 MB', result['steps']['size']['text'])

    def test_program_paths(self):
        result = runner.check_pdf(samples.good(), checks=['pdfunite', 'qpdf'], programs={
            'pdfunite': 'pdfunite-is-not-installed', 'qpdf': '/no/qpdf'})
        self.assertEqual(result['steps']['pdfunite']['state'], 'skipped')
        self.assertEqual(result['steps']['qpdf']['state'], 'skipped')

    def test_unknown_check_fails_before_the_process(self):
        with self.assertRaises(ValueError):
            runner.check_pdf(samples.good(), checks=['spelling'])

    def test_command_line(self):
        path = samples.write('no_text', self.folder)
        output = subprocess.run([sys.executable, '-m', 'graffiti.pdfcheck.checks', path, '--checks', 'open,text'],
                                capture_output=True, env=runner.child_environment(), cwd=self.folder, check=True)
        result = json.loads(output.stdout.decode('utf-8'))
        self.assertEqual(result['findings'], ['no_text'])
