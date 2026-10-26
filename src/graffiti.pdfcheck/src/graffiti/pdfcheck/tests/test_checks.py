""" Tests of the checks in the current process, one per finding. Runs without Plone. """
import importlib.util
import platform
import shutil
import tempfile
import unittest

import pypdf
from graffiti.pdfcheck import checks
from graffiti.pdfcheck.tests import project_checks, samples

HAS_PDFUNITE = shutil.which('pdfunite') is not None
HAS_QPDF = shutil.which('qpdf') is not None
# pypdf reads AES with cryptography or with pycryptodome
HAS_AES = any(importlib.util.find_spec(name) for name in ('cryptography', 'Crypto'))
# pypdf repairs a missing offset of the cross reference table since 6.13.0
PYPDF_REPAIRS_XREF = tuple(int(part) for part in pypdf.__version__.split('.')[:2]) >= (6, 13)
LOST = ['lost_outlines', 'lost_form_fields', 'lost_signatures', 'lost_embedded_files']


def states(result):
    return {name: step['state'] for name, step in result['steps'].items()}


class SampleTestCase(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='pdfcheck-test-')
        self.addCleanup(shutil.rmtree, self.folder)

    def check(self, name, **arguments):
        return checks.run_checks(samples.write(name, self.folder), **arguments)


class TestChecks(SampleTestCase):

    def test_good_file_is_suitable(self):
        result = self.check('good')
        self.assertIs(result['is_pdf'], True)
        self.assertIs(result['suitable'], True)
        self.assertEqual(result['findings'], [])
        # nothing to lose, so no hints
        self.assertEqual(result['hints'], [])
        self.assertEqual(states(result), {
            'header': 'ok', 'open': 'ok', 'text': 'ok', 'rewrite': 'ok',
            'pdfunite': 'ok' if HAS_PDFUNITE else 'skipped', 'qpdf': 'ok' if HAS_QPDF else 'skipped'})
        self.assertEqual(result['pages'], 2)
        self.assertEqual(result['versions']['pypdf'], pypdf.__version__)
        self.assertEqual(result['versions']['python'], platform.python_version())
        if HAS_QPDF:
            self.assertRegex(result['versions']['qpdf'], r'^\d+\.\d+')
        self.assertTrue(result['checked_at'])
        self.assertIsInstance(result['seconds'], float)

    def test_not_pdf_has_no_finding(self):
        result = self.check('not_pdf')
        self.assertIs(result['is_pdf'], False)
        self.assertIsNone(result['suitable'])
        self.assertEqual(result['findings'], [])
        self.assertEqual(states(result), {'header': 'skipped'})

    def test_damaged(self):
        result = self.check('damaged')
        self.assertIs(result['suitable'], False)
        self.assertEqual(result['findings'][0], 'damaged')
        self.assertEqual(states(result)['text'], 'skipped')
        self.assertEqual(states(result)['rewrite'], 'skipped')

    @unittest.skipIf(PYPDF_REPAIRS_XREF, 'pypdf repairs the cross reference table')
    def test_broken_xref_is_damaged(self):
        result = self.check('broken_xref', checks=['open'])
        self.assertEqual(result['findings'], ['damaged'])

    @unittest.skipUnless(PYPDF_REPAIRS_XREF, 'pypdf does not repair the cross reference table')
    def test_broken_xref_is_repaired(self):
        result = self.check('broken_xref', checks=['open', 'text', 'rewrite'])
        self.assertIs(result['suitable'], True)

    def test_password(self):
        result = self.check('password', checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['password'])
        self.assertEqual(states(result)['text'], 'skipped')

    def test_edit_protection(self):
        result = self.check('edit_protection', checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['edit_protection'])
        self.assertIn('opens without a password', result['steps']['open']['text'])
        self.assertEqual(result['pages'], 2)

    @unittest.skipIf(HAS_AES, 'pypdf can read AES here')
    def test_aes_without_cryptography(self):
        result = self.check('aes', checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['edit_protection', 'crypto_missing'])
        self.assertNotIn('damaged', result['findings'])

    @unittest.skipUnless(HAS_AES, 'pypdf can not read AES here')
    def test_aes_with_cryptography(self):
        result = self.check('aes', checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['edit_protection'])

    def test_no_text(self):
        result = self.check('no_text', checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['no_text'])

    def test_rewrite(self):
        result = self.check('rewrite', checks=['open', 'text', 'rewrite'])
        self.assertEqual(result['findings'], ['rewrite'])

    @unittest.skipUnless(HAS_PDFUNITE, 'pdfunite is not installed')
    def test_pdfunite_leaves_out_pages(self):
        result = self.check('pdfunite')
        self.assertEqual(result['findings'], ['pdfunite'])
        self.assertIn('pages lost', result['steps']['pdfunite']['text'])

    @unittest.skipUnless(HAS_PDFUNITE, 'pdfunite is not installed')
    def test_pdfunite_fails(self):
        result = self.check('edit_protection')
        self.assertEqual(result['findings'], ['edit_protection', 'pdfunite'])
        self.assertIn('encrypted', result['steps']['pdfunite']['text'])

    def test_pdfunite_missing_is_skipped(self):
        """ A missing program is no finding, as long as other checks ran """
        result = self.check('good', checks=['open', 'pdfunite'], programs={'pdfunite': 'pdfunite-is-not-installed'})
        self.assertIs(result['suitable'], True)
        self.assertEqual(result['steps']['pdfunite']['state'], 'skipped')
        self.assertIn('not installed', result['steps']['pdfunite']['text'])

    @unittest.skipUnless(HAS_QPDF, 'qpdf is not installed')
    def test_qpdf_errors(self):
        result = self.check('damaged', checks=['qpdf'])
        self.assertEqual(result['findings'], ['qpdf'])
        self.assertIn('damaged.pdf', result['steps']['qpdf']['text'])
        self.assertNotIn(self.folder, result['steps']['qpdf']['text'])

    @unittest.skipUnless(HAS_QPDF, 'qpdf is not installed')
    def test_qpdf_warnings_are_a_hint(self):
        result = self.check('broken_xref', checks=['qpdf'])
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['hints'], ['qpdf_warnings'])
        self.assertEqual(result['steps']['qpdf']['state'], 'hint')
        self.assertIs(result['suitable'], True)

    def test_qpdf_missing_is_skipped(self):
        result = self.check('damaged', checks=['qpdf'], programs={'qpdf': 'qpdf-is-not-installed'})
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['steps']['qpdf']['state'], 'skipped')
        self.assertIn('not installed', result['steps']['qpdf']['text'])


class TestLostFeatures(SampleTestCase):
    """ Hints for what rebuilding or appending loses, only for what the file has """

    def test_rewrite_loses_everything(self):
        result = self.check('features', checks=['open', 'rewrite'])
        self.assertIs(result['suitable'], True)
        self.assertEqual(result['hints'], LOST)
        self.assertEqual(result['steps']['rewrite']['state'], 'hint')
        self.assertEqual(result['steps']['rewrite']['text'], (
            'pages and metadata complete; lost: 1 of 1 bookmark, 1 of 1 form field, 1 of 1 signature, '
            '1 of 1 embedded file'))

    @unittest.skipUnless(HAS_PDFUNITE, 'pdfunite is not installed')
    def test_pdfunite_keeps_the_pages(self):
        result = self.check('features', checks=['pdfunite'])
        self.assertIs(result['suitable'], True)
        # what pdfunite loses depends on the version of Poppler, 24.02 loses only the bookmarks
        self.assertTrue(set(result['hints']) <= set(LOST))


class TestCheckList(SampleTestCase):

    def test_only_given_checks_run(self):
        result = self.check('no_text', checks=['rewrite'])
        self.assertEqual(states(result), {'header': 'ok', 'rewrite': 'ok'})
        self.assertIs(result['suitable'], True)

    def test_nothing_checked_is_not_suitable(self):
        """ pypdf can not open the file and the check "open" is switched off """
        result = self.check('damaged', checks=['text', 'rewrite'])
        self.assertEqual(states(result), {'header': 'ok', 'text': 'skipped', 'rewrite': 'skipped'})
        self.assertEqual(result['hints'], ['not_checked'])
        self.assertIsNone(result['suitable'])

    def test_unknown_check(self):
        with self.assertRaises(ValueError):
            checks.resolve_checks(['spelling'])

    def test_check_of_a_project(self):
        result = self.check('good', checks=['open', 'graffiti.pdfcheck.tests.project_checks.ONE_PAGE'])
        self.assertEqual(result['findings'], ['too_many_pages'])
        self.assertEqual(result['steps']['one_page']['text'], '2 pages, allowed is 1')

    def test_check_given_as_object(self):
        result = self.check('good', checks=[project_checks.ONE_PAGE])
        self.assertEqual(result['findings'], ['too_many_pages'])

    def test_check_given_as_spec(self):
        """ The way the runner hands a check of a project to the check process """
        spec = checks.check_spec(project_checks.ONE_PAGE)
        self.assertEqual(spec, {'name': 'one_page', 'tool': 'pypdf', 'finding': 'too_many_pages',
                                'module': 'graffiti.pdfcheck.tests.project_checks', 'function': 'check_one_page'})
        [check] = checks.resolve_checks([spec])
        self.assertIs(check.function, project_checks.check_one_page)

    def test_function_of_a_check_must_be_importable(self):
        local = checks.Check('local', 'script', 'local', lambda context: checks.ok('done'))
        with self.assertRaises(ValueError):
            checks.check_spec(local)

    def test_error_in_a_check_is_its_finding(self):
        result = self.check('good', checks=['graffiti.pdfcheck.tests.project_checks.BROKEN'])
        self.assertEqual(result['findings'], ['broken'])
        self.assertEqual(result['steps']['broken']['text'], 'ZeroDivisionError: division by zero')
