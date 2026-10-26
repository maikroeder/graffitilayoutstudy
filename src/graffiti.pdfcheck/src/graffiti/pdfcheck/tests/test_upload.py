""" The ways of uploading a file in Plone, each through a real request """
import base64
import io
import json
import unittest

import plone.api as api
import transaction
from graffiti.pdfcheck import api as pdfcheck
from graffiti.pdfcheck.testing import GRAFFITI_PDFCHECK_FUNCTIONAL_TESTING
from graffiti.pdfcheck.tests import samples
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser

BOUNDARY = 'graffiti-pdfcheck-boundary'


def multipart(field, filename, data):
    head = ('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
            'Content-Type: application/pdf\r\n\r\n' % (BOUNDARY, field, filename)).encode('ascii')
    return head + data + ('\r\n--%s--\r\n' % BOUNDARY).encode('ascii')


class TestUploadWays(unittest.TestCase):
    layer = GRAFFITI_PDFCHECK_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        transaction.commit()

    def browser(self):
        browser = Browser(self.layer['app'])
        browser.handleErrors = False
        browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        return browser

    def result(self, obj_id):
        transaction.begin()
        return pdfcheck.get_result(self.portal[obj_id])

    def test_add_form(self):
        browser = self.browser()
        browser.open(self.portal_url + '/++add++File')
        browser.getControl(name='form.widgets.file').add_file(
            io.BytesIO(samples.edit_protection()), 'application/pdf', 'protected.pdf')
        browser.getControl(name='form.buttons.save').click()
        # the status message after saving, and the viewlet in the view of the file
        self.assertIn('the file was saved, but it can probably not be processed later', browser.contents)
        self.assertIn('PDF check: this file can probably not be processed later.', browser.contents)
        self.assertIn('edit_protection', self.result('protected.pdf')['findings'])

    def test_edit_form_with_a_new_file(self):
        browser = self.browser()
        browser.open(self.portal_url + '/++add++File')
        browser.getControl(name='form.widgets.file').add_file(io.BytesIO(samples.no_text()), 'application/pdf', 'f.pdf')
        browser.getControl(name='form.buttons.save').click()
        self.assertEqual(self.result('f.pdf')['findings'], ['no_text'])
        browser.open(self.portal_url + '/f.pdf/edit')
        browser.getControl(name='form.widgets.file.action').value = ['replace']
        browser.getControl(name='form.widgets.file').add_file(io.BytesIO(samples.good()), 'application/pdf', 'f.pdf')
        browser.getControl(name='form.buttons.save').click()
        self.assertEqual(self.result('f.pdf')['findings'], [])
        self.assertNotIn('graffiti-pdfcheck', browser.contents)

    def test_upload_in_the_folder_view(self):
        """ The upload of the folder contents and of TinyMCE both post to @@fileUpload """
        browser = self.browser()
        browser.post(self.portal_url + '/@@fileUpload', multipart('file', 'upload.pdf', samples.no_text()),
                     'multipart/form-data; boundary=%s' % BOUNDARY)
        name = json.loads(browser.contents)['name']
        self.assertEqual(self.result(name)['findings'], ['no_text'])

    def test_save_settings_with_a_type_that_is_not_offered(self):
        api.portal.set_registry_record('graffiti.pdfcheck.portal_types', ['File', 'Document'])
        transaction.commit()
        browser = self.browser()
        browser.open(self.portal_url + '/@@pdfcheck-settings')
        self.assertEqual(browser.getControl(name='form.widgets.portal_types:list').value, ['File'])
        browser.getControl(name='form.buttons.save').click()
        self.assertIn('Changes saved', browser.contents)
        transaction.begin()
        self.assertEqual(api.portal.get_registry_record('graffiti.pdfcheck.portal_types'), ['File'])

    def test_rest_api(self):
        browser = self.browser()
        browser.addHeader('Accept', 'application/json')
        browser.post(self.portal_url, json.dumps({
            '@type': 'File',
            'id': 'api.pdf',
            'title': 'api.pdf',
            'file': {
                'data': base64.b64encode(samples.no_text()).decode('ascii'),
                'encoding': 'base64',
                'filename': 'api.pdf',
                'content-type': 'application/pdf',
            },
        }), 'application/json')
        self.assertEqual(browser.headers['status'].split()[0], '201')
        self.assertEqual(self.result('api.pdf')['findings'], ['no_text'])
        # no status message for the REST API, it would only show up on the next page
        self.assertNotIn('statusmessages', browser.cookies)
