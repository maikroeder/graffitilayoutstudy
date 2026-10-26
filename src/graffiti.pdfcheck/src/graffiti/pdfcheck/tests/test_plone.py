""" The check in Plone: when it runs, what it stores, what editors see. """
import os
from copy import deepcopy

import plone.api as api
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.Guard import Guard
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from graffiti.pdfcheck import api as pdfcheck
from graffiti.pdfcheck.checks import add_step, finding, finish, new_result, ok
from graffiti.pdfcheck.api import check_object
from graffiti.pdfcheck.interfaces import IGraffitiPdfcheckLayer, IPdfCheck, IPdfCheckRunner
from graffiti.pdfcheck.messages import FINDING_LABELS, _, hint_texts
from graffiti.pdfcheck.settings import get_checks
from graffiti.pdfcheck.testing import GRAFFITI_PDFCHECK_INTEGRATION_TESTING
from graffiti.pdfcheck.tests import project_checks, samples
from graffiti.pdfcheck.viewlets.pdfcheck import INFO_CLASSES, WARNING_CLASSES
from interaktiv.framework.test import TestCase
from plone.app.contenttypes.interfaces import IFile
from plone.app.testing import logout
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from zope.component import getGlobalSiteManager, getMultiAdapter, getUtility, queryMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.lifecycleevent import Attributes, ObjectModifiedEvent
from zope.viewlet.interfaces import IViewletManager


def make_result(findings=(), hints=()):
    result = new_result()
    result['is_pdf'] = True
    add_step(result, 'header', 'script', ok('found'))
    for code in findings:
        add_step(result, 'open', 'pypdf', finding(code))
    if not findings:
        add_step(result, 'open', 'pypdf', ok('2 pages'))
    if hints:
        add_step(result, 'rewrite', 'pypdf', ok('pages and metadata complete; lost: 1 of 1 bookmark', list(hints)))
    return finish(result)


class FakeRunner(object):
    """ Stands for the runner of a project, for example an external service """

    def __init__(self, result=None, error=None):
        self.calls = []
        self.result = result if result is not None else make_result()
        self.error = error

    def check(self, path, settings):
        self.calls.append(settings)
        if self.error:
            raise self.error
        return deepcopy(self.result)


class PloneTestCase(TestCase):
    layer = GRAFFITI_PDFCHECK_INTEGRATION_TESTING

    def add_file(self, data, name='sample.pdf', container=None):
        return api.content.create(
            container=container or self.portal, type='File', id=name, title=name,
            file=NamedBlobFile(data=data, filename=name, contentType='application/pdf'))

    def register_check(self, check):
        """ The way a project registers its check in its configure.zcml """
        site_manager = getGlobalSiteManager()
        site_manager.registerUtility(check, IPdfCheck, check.name)
        self.addCleanup(site_manager.unregisterUtility, check, IPdfCheck, check.name)

    def use_runner(self, runner):
        # a local utility, the way a project can replace the runner in its own profile
        self.portal.getSiteManager().registerUtility(runner, IPdfCheckRunner)
        self.addCleanup(self.portal.getSiteManager().unregisterUtility, runner, IPdfCheckRunner)
        return runner

    def set_setting(self, name, value):
        api.portal.set_registry_record('graffiti.pdfcheck.' + name, value)

    def messages(self):
        return [(message.message, message.type) for message in IStatusMessage(self.request).show()]


class TestCheckOnUpload(PloneTestCase):
    """ With the real runner: the checks run in their own process """

    def test_good_file(self):
        obj = self.add_file(samples.good())
        result = pdfcheck.get_result(obj)
        self.assertIs(result['suitable'], True)
        self.assertEqual(result['findings'], [])
        self.assertEqual(result['filename'], 'sample.pdf')
        self.assertEqual(result['field'], 'file')
        self.assertEqual(len(result['sha256']), 64)
        self.assertEqual(result['size'], len(samples.good()))
        self.assertEqual(self.messages(), [])

    def test_file_with_findings(self):
        obj = self.add_file(samples.edit_protection())
        self.assertIs(pdfcheck.is_suitable(obj), False)
        self.assertIn('edit_protection', pdfcheck.get_findings(obj))
        [(message, message_type)] = self.messages()
        self.assertEqual(message_type, 'warning')
        self.assertIn('the file was saved, but it can probably not be processed later. '
                      'The file has an edit protection.', message)

    def test_too_large_file_is_not_checked(self):
        self.set_setting('max_size_mb', 1)
        obj = self.add_file(samples.good() + b'%' * (1024 * 1024))
        result = pdfcheck.get_result(obj)
        self.assertIsNone(result['suitable'])
        self.assertEqual(result['hints'], ['not_checked'])
        [(message, message_type)] = self.messages()
        self.assertEqual(message_type, 'info')
        self.assertIn('Please note: The file was not checked.', message)

    def test_registered_check_of_a_project(self):
        self.register_check(project_checks.ONE_PAGE)
        self.set_setting('checks', ['open', 'one_page'])
        obj = self.add_file(samples.good())
        result = pdfcheck.get_result(obj)
        self.assertEqual(list(result['steps']), ['header', 'open', 'one_page'])
        self.assertEqual(result['findings'], ['too_many_pages'])
        # the sentence of the check for its finding
        [(message, message_type)] = self.messages()
        self.assertIn('can probably not be processed later. The file may only have one page.', message)

    def test_unknown_check_in_the_settings(self):
        """ A check of a removed package is left out, the other checks run """
        self.set_setting('checks', ['open', 'spelling'])
        obj = self.add_file(samples.good())
        result = pdfcheck.get_result(obj)
        self.assertIs(result['suitable'], True)
        self.assertEqual(list(result['steps']), ['header', 'open'])

    def test_program_paths_from_the_environment(self):
        os.environ['GRAFFITI_PDFCHECK_QPDF'] = 'qpdf-is-not-installed'
        self.addCleanup(os.environ.pop, 'GRAFFITI_PDFCHECK_QPDF')
        self.set_setting('checks', ['open', 'qpdf'])
        obj = self.add_file(samples.good())
        self.assertEqual(pdfcheck.get_result(obj)['steps']['qpdf']['state'], 'skipped')

    def test_no_program_paths_in_the_settings(self):
        """ Whoever may change the settings must not be able to start a program on the server """
        registry = getUtility(IRegistry)
        self.assertNotIn('graffiti.pdfcheck.qpdf', registry.records)
        self.assertNotIn('graffiti.pdfcheck.pdfunite', registry.records)


class TestWhenTheCheckRuns(PloneTestCase):

    def setUp(self):
        super(TestWhenTheCheckRuns, self).setUp()
        self.runner = self.use_runner(FakeRunner())

    def test_settings_reach_the_runner(self):
        self.set_setting('timeout', 5)
        self.add_file(samples.good())
        [settings] = self.runner.calls
        self.assertEqual(settings['timeout'], 5)
        self.assertEqual(settings['programs'], {'pdfunite': 'pdfunite', 'qpdf': 'qpdf'})

    def test_checks_of_a_project_run_after_the_built_in_checks(self):
        self.register_check(project_checks.ONE_PAGE)
        self.set_setting('checks', ['one_page', 'qpdf', 'open'])
        self.add_file(samples.good())
        [settings] = self.runner.calls
        self.assertEqual(settings['checks'], ['one_page', 'qpdf', 'open'])
        self.assertEqual([check.name for check in get_checks(settings['checks'])], ['open', 'qpdf', 'one_page'])

    def test_not_pdf_stays_untouched(self):
        obj = self.add_file(samples.not_pdf(), name='notes.pdf')
        self.assertEqual(self.runner.calls, [])
        self.assertIsNone(pdfcheck.get_result(obj))
        self.assertIsNone(pdfcheck.is_suitable(obj))

    def test_switched_off(self):
        self.set_setting('enabled', False)
        obj = self.add_file(samples.good())
        self.assertEqual(self.runner.calls, [])
        self.assertIsNone(pdfcheck.get_result(obj))

    def test_switched_off_removes_the_result_of_an_older_file(self):
        """ Otherwise a workflow would decide on the result of the file before """
        self.runner.result = make_result(findings=['damaged'])
        obj = self.add_file(samples.damaged())
        self.set_setting('enabled', False)
        obj.file = NamedBlobFile(data=samples.good(), filename='good.pdf', contentType='application/pdf')
        notify(ObjectModifiedEvent(obj, Attributes(IFile, 'file')))
        self.assertIsNone(pdfcheck.get_result(obj))
        self.assertIsNone(pdfcheck.is_suitable(obj))

    def test_check_that_could_not_run_is_repeated(self):
        """ A time limit says nothing about the file: the same file is checked again """
        self.runner.result = make_result(findings=['timeout'])
        obj = self.add_file(samples.good())
        self.runner.result = make_result()
        obj.file = NamedBlobFile(data=samples.good(), filename='again.pdf', contentType='application/pdf')
        notify(ObjectModifiedEvent(obj, Attributes(IFile, 'file')))
        self.assertEqual(len(self.runner.calls), 2)
        self.assertIs(pdfcheck.is_suitable(obj), True)

    def test_too_large_file_is_not_read(self):
        self.set_setting('max_size_mb', 1)
        obj = self.add_file(samples.good() + b'%' * (1024 * 1024))
        self.assertEqual(self.runner.calls, [])
        result = pdfcheck.get_result(obj)
        self.assertEqual(result['hints'], ['not_checked'])
        self.assertIsNone(result['sha256'])

    def test_conflict_error_of_the_runner_is_raised(self):
        """ Zope repeats the request """
        self.runner.error = ConflictError()
        with self.assertRaises(ConflictError):
            self.add_file(samples.good())

    def test_other_content_types(self):
        self.set_setting('portal_types', ['Document'])
        self.add_file(samples.good())
        self.assertEqual(self.runner.calls, [])

    def test_changed_title_is_no_new_check(self):
        obj = self.add_file(samples.good())
        obj.title = 'Another title'
        notify(ObjectModifiedEvent(obj, Attributes(IFile, 'IDublinCore.title')))
        self.assertEqual(len(self.runner.calls), 1)

    def test_new_file_is_checked(self):
        obj = self.add_file(samples.good())
        obj.file = NamedBlobFile(data=samples.no_text(), filename='other.pdf', contentType='application/pdf')
        notify(ObjectModifiedEvent(obj, Attributes(IFile, 'file')))
        self.assertEqual(len(self.runner.calls), 2)
        self.assertEqual(pdfcheck.get_result(obj)['filename'], 'other.pdf')

    def test_same_file_is_no_new_check(self):
        """ Without the names of the changed fields the checksum decides """
        obj = self.add_file(samples.good())
        obj.file = NamedBlobFile(data=samples.good(), filename='again.pdf', contentType='application/pdf')
        notify(ObjectModifiedEvent(obj))
        self.assertEqual(len(self.runner.calls), 1)

    def test_copy_keeps_the_result(self):
        obj = self.add_file(samples.good())
        copy = api.content.copy(source=obj, target=self.portal, id='copy.pdf')
        self.assertEqual(len(self.runner.calls), 1)
        self.assertEqual(pdfcheck.get_result(copy)['sha256'], pdfcheck.get_result(obj)['sha256'])

    def test_removed_file_removes_the_result(self):
        obj = self.add_file(samples.good())
        obj.file = None
        notify(ObjectModifiedEvent(obj, Attributes(IFile, 'file')))
        self.assertIsNone(pdfcheck.get_result(obj))

    def test_check_again(self):
        obj = self.add_file(samples.good())
        self.assertIsNone(check_object(obj))
        self.assertIsNotNone(check_object(obj, force=True))
        self.assertEqual(len(self.runner.calls), 2)

    def test_error_of_the_runner_does_not_stop_the_upload(self):
        self.runner.error = RuntimeError('service not reachable')
        obj = self.add_file(samples.good())
        result = pdfcheck.get_result(obj)
        self.assertEqual(result['hints'], ['not_checked'])
        self.assertIn('service not reachable', result['steps']['runner']['text'])

    def test_message_for_hints(self):
        self.runner.result = make_result(hints=['lost_outlines'])
        self.add_file(samples.good())
        [(message, message_type)] = self.messages()
        self.assertEqual(message_type, 'info')
        self.assertEqual(message, 'PDF check: the file was saved. Please note: '
                                  'When the file is processed, these are lost: bookmarks.')


class TestApi(PloneTestCase):
    guard = "python: here.restrictedTraverse('@@pdfcheck').suitable() is not False"

    def setUp(self):
        super(TestApi, self).setUp()
        self.runner = self.use_runner(FakeRunner(make_result(findings=['no_text'])))

    def check_guard(self, obj):
        guard = Guard()
        guard.changeFromProperties({'guard_expr': self.guard})
        workflow = getToolByName(self.portal, 'portal_workflow')['simple_publication_workflow']
        return guard.check(getSecurityManager(), workflow, obj)

    def test_api(self):
        obj = self.add_file(samples.good())
        self.assertIs(pdfcheck.is_suitable(obj), False)
        self.assertEqual(pdfcheck.get_findings(obj), ['no_text'])
        self.assertEqual(pdfcheck.get_hints(obj), [])

    def test_view(self):
        obj = self.add_file(samples.good())
        view = obj.restrictedTraverse('@@pdfcheck')
        self.assertIs(view.suitable(), False)
        self.assertTrue(view.has_finding('no_text'))
        self.assertIn('"findings": ["no_text"]', view())

    def test_guard_of_a_workflow(self):
        self.assertFalse(self.check_guard(self.add_file(samples.good())))
        self.runner.result = make_result()
        self.assertTrue(self.check_guard(self.add_file(samples.good(), name='good.pdf')))
        # files without a result, for example uploaded before the installation
        self.assertTrue(self.check_guard(api.content.create(container=self.portal, type='Document', id='page')))


class TestViewlet(PloneTestCase):

    def setUp(self):
        super(TestViewlet, self).setUp()
        alsoProvides(self.request, IGraffitiPdfcheckLayer)
        self.runner = self.use_runner(FakeRunner(make_result(findings=['no_text'], hints=['lost_outlines'])))

    def render(self, obj):
        view = getMultiAdapter((obj, self.request), name='view')
        manager = queryMultiAdapter((obj, self.request, view), IViewletManager, name='plone.abovecontentbody')
        manager.update()
        return manager.render()

    def test_findings_and_hints(self):
        html = self.render(self.add_file(samples.good()))
        self.assertIn(WARNING_CLASSES, html)
        self.assertIn('PDF check: this file can probably not be processed later.', html)
        self.assertIn('No text can be read from the file, for example because it is a scan.', html)
        self.assertIn('Please also note:', html)
        self.assertIn('When the file is processed, these are lost: bookmarks.', html)
        # the words of the programs only in the technical details
        self.assertIn('<summary>Technical details</summary>', html)
        self.assertIn('<strong>Rebuild page by page</strong>: pages and metadata complete', html)
        self.assertIn('++resource++graffiti.pdfcheck/pdfcheck.css', html)

    def test_check_of_a_project(self):
        """ The sentence of the check for its finding, its title in the technical details """
        self.register_check(project_checks.ONE_PAGE)
        result = make_result()
        add_step(result, 'one_page', 'pypdf', finding('too_many_pages', '2 pages, allowed is 1'))
        self.runner.result = finish(result)
        html = self.render(self.add_file(samples.good()))
        self.assertIn('The file may only have one page.', html)
        self.assertIn('<strong>Only one page per file</strong>: 2 pages, allowed is 1', html)

    def test_check_of_a_project_without_texts(self):
        """ Without texts the code of the finding and the name of the check are shown """
        self.register_check(project_checks.ONE_PAGE._replace(title=None, texts=None))
        result = make_result()
        add_step(result, 'one_page', 'pypdf', finding('too_many_pages', '2 pages, allowed is 1'))
        self.runner.result = finish(result)
        html = self.render(self.add_file(samples.good()))
        self.assertIn('<li>too_many_pages</li>', html)
        self.assertIn('<strong>one_page</strong>: 2 pages, allowed is 1', html)

    def test_only_hints(self):
        self.runner.result = make_result(hints=['lost_outlines'])
        html = self.render(self.add_file(samples.good()))
        self.assertIn(INFO_CLASSES, html)
        self.assertIn('PDF check: please note', html)
        self.assertNotIn('Please also note:', html)
        self.assertIn('When the file is processed, these are lost: bookmarks.', html)

    def test_nothing_without_findings(self):
        self.runner.result = make_result()
        self.assertNotIn('graffiti-pdfcheck', self.render(self.add_file(samples.good())))

    def test_only_for_editors(self):
        obj = self.add_file(samples.good())
        logout()
        self.assertNotIn('graffiti-pdfcheck', self.render(obj))

    def test_switched_off(self):
        obj = self.add_file(samples.good())
        self.set_setting('enabled', False)
        self.assertNotIn('graffiti-pdfcheck', self.render(obj))


class TestTranslations(PloneTestCase):

    def test_german(self):
        self.assertEqual(translate(FINDING_LABELS['no_text'], target_language='de'),
                         'Aus der Datei lässt sich kein Text lesen, zum Beispiel weil sie ein Scan ist.')

    def test_lost_parts_in_one_sentence(self):
        self.assertEqual(hint_texts(['qpdf_warnings', 'lost_outlines', 'lost_signatures'], self.request), [
            'The inner structure has small errors that can be repaired automatically.',
            'When the file is processed, these are lost: bookmarks, signatures.'])
        self.assertEqual(translate(_('hint_lost', mapping={'items': 'Lesezeichen'}), target_language='de'),
                         'Bei der Weiterverarbeitung gehen verloren: Lesezeichen.')
