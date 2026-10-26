""" The upload utility of interaktiv.basetiles without stopping the upload, see utilities/upload_file.py """
import os
import shutil
import tempfile
import unittest
from unittest import mock

import graffiti.pdf_preview_fix
import zope.component
from graffiti.pdf_preview_fix.utilities.upload_file import UploadFileUtilityWithoutPreviewError
from interaktiv.basetiles.utilities.upload_file import IUploadFileUtility
from zope.component import getUtility
from zope.component.testing import setUp, tearDown
from zope.configuration import xmlconfig

# a PDF file without page tree and cross reference table, gm can not read it
DAMAGED_PDF = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF\n'


class TestUploadFile(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.utility = UploadFileUtilityWithoutPreviewError()

    def tearDown(self):
        shutil.rmtree(self.folder)

    def write(self, name, data):
        path = os.path.join(self.folder, name)
        with open(path, 'wb') as output:
            output.write(data)
        return path

    def test_damaged_pdf_has_no_preview_image(self):
        self.assertIsNone(self.utility.get_image_blob(self.write('damaged.pdf', DAMAGED_PDF)))

    def test_missing_gm(self):
        path = self.write('damaged.pdf', DAMAGED_PDF)
        with mock.patch('subprocess.check_call', side_effect=FileNotFoundError):
            self.assertIsNone(self.utility.get_image_blob(path))

    def test_other_errors_stay(self):
        with self.assertRaises(FileNotFoundError):
            self.utility.get_image_blob(os.path.join(self.folder, 'missing.pdf'))


class TestRegistration(unittest.TestCase):

    def setUp(self):
        setUp()

    def tearDown(self):
        tearDown()

    def test_overrides_replace_the_utility(self):
        context = xmlconfig.file('meta.zcml', zope.component)
        xmlconfig.file('overrides.zcml', graffiti.pdf_preview_fix, context=context)
        self.assertIsInstance(getUtility(IUploadFileUtility), UploadFileUtilityWithoutPreviewError)
