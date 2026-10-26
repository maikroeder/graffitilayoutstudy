import os
import re
import tempfile
import zipfile

from interaktiv.basetiles import _
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from plone.supermodel.directives import primary
from zope import schema
from zope.interface import Invalid
from zope.interface import implementer
from zope.schema import ValidationError

ZIP_MIMETYPES = [
    'application/zip',
    'application/x-zip-compressed',
]


def check_valid_zip_mimetype(value):
    """Validate that uploaded file is a ZIP file"""
    mimetype = value.contentType
    if mimetype not in ZIP_MIMETYPES:
        raise Invalid(_('trans_message_zipfile_wrong_type',
                        default='Ungültiger Dateityp. Erlaubte Formate: ZIP',
                        mapping={'mimetype': mimetype}))
    return True


def validate_webmirror_id(value):
    """Validate that webmirror_id contains only alphanumeric characters"""
    if not re.match(r'^[a-zA-Z0-9]+$', value):
        raise Invalid(_('trans_message_webmirror_id_invalid',
                                default='WebMirror ID darf nur alphanumerische Zeichen enthalten'))
    return True


class IWebmirror(model.Schema):
    """Schema for WebMirror content type"""

    webmirror_id = schema.TextLine(
        title=_(
            'trans_label_webmirror_id',
            default='WebMirror ID',
        ),
        description=_(
            'trans_desc_webmirror_id',
            default='Alphanumerische Bezeichnung für den Ordnernamen (z.B. websitev19)'
        ),
        required=True,
        constraint=validate_webmirror_id
    )

    primary('zipfile')
    zipfile = NamedBlobFile(
        title=_(
            'trans_label_zip_file',
            default='ZIP Datei'
        ),
        description=_(
            'trans_desc_zip_file',
            default='ZIP Datei mit Website-Mirror (HTML, CSS, Bilder usw.)'
        ),
        required=True,
        constraint=check_valid_zip_mimetype
    )


@implementer(IWebmirror)
class Webmirror(Container):
    """WebMirror content type for hosting website mirrors"""

    @property
    def title(self):
        return self.webmirror_id

    @title.setter
    def title(self, webmirror_id):
        pass

    @staticmethod
    def _get_base_path():
        buildout_dir = os.environ.get('BUILDOUT_DIR', '/tmp')
        return os.path.join(buildout_dir, 'var', 'webmirrors')

    def _get_extraction_path(self, webmirror_id):
        return os.path.join(self._get_base_path(), webmirror_id)

    def _cache_exists(self, webmirror_id):
        path = self._get_extraction_path(webmirror_id)
        return os.path.exists(path) and os.path.isdir(path)

    def _prepare_extraction_directory(self, webmirror_id):
        base_dir = self._get_base_path()
        extraction_dir = self._get_extraction_path(webmirror_id)

        os.makedirs(base_dir, exist_ok=True)

        if os.path.exists(extraction_dir):
            import shutil
            shutil.rmtree(extraction_dir)

        os.makedirs(extraction_dir, exist_ok=True)

        return extraction_dir

    @staticmethod
    def _extract_zip_to_directory(zip_data, extraction_dir):
        with tempfile.NamedTemporaryFile(delete=False) as temp_zip:
            temp_zip.write(zip_data.data)
            temp_zip_path = temp_zip.name

        # TODO: Does this make sense??
        try:
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                for member in zip_ref.namelist():
                    if os.path.isabs(member) or ".." in member:
                        continue
                    zip_ref.extract(member, extraction_dir)
        finally:
            os.unlink(temp_zip_path)

    def get_webmirror(self):
        webmirror_id = getattr(self, 'webmirror_id', None)
        zip_file = getattr(self, 'zipfile', None)

        if not webmirror_id or not zip_file:
            return None

        if self._cache_exists(webmirror_id):
            return self._get_extraction_path(webmirror_id)
        else:
            return self.extract_webmirror(webmirror_id)

    def extract_webmirror(self, force=False):
        webmirror_id = getattr(self, 'webmirror_id', None)
        zip_file = getattr(self, 'zipfile', None)

        if not webmirror_id or not zip_file:
            return None

        if not force and self._cache_exists(webmirror_id):
            return self._get_extraction_path(webmirror_id)

        try:
            extraction_dir = self._prepare_extraction_directory(webmirror_id)
            self._extract_zip_to_directory(zip_file, extraction_dir)
            return extraction_dir

        except Exception as e:
            print(e)
            return None
