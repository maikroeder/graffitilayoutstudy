""" Small sample files for the tests, one per finding. Made in code, so that no real document is needed.

Writes all samples into a folder, for example to upload them in a Plone site:

    python -m graffiti.pdfcheck.tests.samples FOLDER

`files/aes-128.pdf` is stored in the package, because making it needs the Python package cryptography
(see `make_aes`). The other samples need only pypdf, the encryption uses RC4.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AES_FILE = os.path.join(HERE, 'files', 'aes-128.pdf')

FONT = b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>'


def build(objects):
    """ A PDF file from the bodies of its objects, numbered from 1, with a correct cross reference table """
    out = io.BytesIO()
    out.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = []
    for number, body in enumerate(objects, 1):
        offsets.append(out.tell())
        out.write(b'%d 0 obj\n%s\nendobj\n' % (number, body))
    xref = out.tell()
    out.write(b'xref\n0 %d\n0000000000 65535 f \n' % (len(objects) + 1))
    for offset in offsets:
        out.write(b'%010d 00000 n \n' % offset)
    out.write(b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objects) + 1, xref))
    return out.getvalue()


def stream(data, extra=b''):
    return b'<< /Length %d %s>>\nstream\n%s\nendstream' % (len(data), extra, data)


def page_objects(texts, page_extra=b'', count=None, catalog_extra=b''):
    """ Catalog, page tree, font, then a page and its content for each text (None: an empty page) """
    kids = b' '.join(b'%d 0 R' % (4 + 2 * index) for index in range(len(texts)))
    objects = [b'<< /Type /Catalog /Pages 2 0 R %s>>' % catalog_extra,
               b'<< /Type /Pages /Kids [%s] /Count %d >>' % (kids, len(texts) if count is None else count),
               FONT]
    for index, text in enumerate(texts):
        objects.append(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Resources << /Font << /F1 3 0 R >> >> '
                       b'/Contents %d 0 R %s>>' % (5 + 2 * index, page_extra))
        objects.append(stream(b'BT /F1 14 Tf 20 100 Td (%s) Tj ET' % text.encode('ascii') if text else b''))
    return objects


def encrypt(data, algorithm='RC4-128', **arguments):
    from pypdf import PdfReader, PdfWriter
    writer = PdfWriter()
    for page in PdfReader(io.BytesIO(data)).pages:
        writer.add_page(page)
    writer.encrypt(algorithm=algorithm, **arguments)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def good():
    return build(page_objects(['A sample file for the PDF check.', 'This is the second page.']))


def not_pdf():
    return b'A text file with the extension of a PDF.\n'


def damaged():
    data = good()
    return data[:int(len(data) * 0.6)]


def broken_xref():
    """ The offset of the cross reference table is missing. pypdf repairs this since 6.13.0. """
    return good().replace(b'startxref', b'startxref\n1\n%', 1)


def password():
    return encrypt(good(), user_password='secret', owner_password='owner')


def edit_protection():
    from pypdf.constants import UserAccessPermissions
    # opens without a password, printing is allowed, changing is not
    return encrypt(good(), user_password='', owner_password='owner', permissions_flag=UserAccessPermissions.PRINT)


def aes():
    """ Edit protection with AES, the stored file: pypdf needs cryptography to read its text """
    with open(AES_FILE, 'rb') as aes_file:
        return aes_file.read()


def make_aes():
    """ Makes the content of files/aes-128.pdf, needs cryptography """
    return encrypt(good(), algorithm='AES-128', user_password='', owner_password='owner')


def no_text():
    # an empty page stands for a scan: no text to read
    return build(page_objects([None]))


def rewrite():
    """ The page refers to an object that refers to itself. Reading works, copying the page fails. """
    return build(page_objects(['A page that can not be copied.'], page_extra=b'/PieceInfo 6 0 R ') + [b'6 0 R'])


def nested():
    """ The page refers to a dictionary nested 3000 times. Copying the page makes Python 3.8 crash. """
    return build(page_objects(['A page with a deeply nested object.'], page_extra=b'/PieceInfo 6 0 R ') +
                 [b'<< /A ' * 3000 + b'>>' * 3000])


def features():
    """ A bookmark, a form field, a signed signature field and an embedded file: rebuilding the file loses them """
    objects = page_objects(
        ['A page with a form field and a signature.'], page_extra=b'/Annots [9 0 R 10 0 R] ',
        catalog_extra=b'/Outlines 7 0 R /AcroForm << /Fields [9 0 R 10 0 R] /SigFlags 3 >> '
                      b'/Names << /EmbeddedFiles 12 0 R >> ')
    objects += [
        # 6, 7: the bookmark
        b'<< /Title (Chapter 1) /Parent 7 0 R /Dest [4 0 R /Fit] >>',
        b'<< /Type /Outlines /First 6 0 R /Last 6 0 R /Count 1 >>',
        # 8: the value of the signature, not a real one
        b'<< /Type /Sig /Filter /Adobe.PPKLite /SubFilter /adbe.pkcs7.detached /ByteRange [0 0 0 0] /Contents <00> >>',
        # 9, 10: a text field and a signature field
        b'<< /FT /Tx /T (name) /V (Jane) /Type /Annot /Subtype /Widget /Rect [20 20 120 40] /P 4 0 R >>',
        b'<< /FT /Sig /T (signature) /V 8 0 R /Type /Annot /Subtype /Widget /Rect [0 0 0 0] /P 4 0 R >>',
        # 11 to 13: the embedded file
        stream(b'A note in the PDF.', b'/Type /EmbeddedFile '),
        b'<< /Names [(note.txt) 13 0 R] >>',
        b'<< /Type /Filespec /F (note.txt) /UF (note.txt) /EF << /F 11 0 R >> >>',
    ]
    return build(objects)


def pdfunite():
    """ The page tree says 0 pages. pypdf finds the page, pdfunite leaves it out without an error. """
    return build(page_objects(['A page that pdfunite leaves out.'], count=0))


SAMPLES = {
    'good': good,
    'not_pdf': not_pdf,
    'damaged': damaged,
    'broken_xref': broken_xref,
    'password': password,
    'edit_protection': edit_protection,
    'aes': aes,
    'no_text': no_text,
    'rewrite': rewrite,
    'nested': nested,
    'features': features,
    'pdfunite': pdfunite,
}


def write(name, folder):
    """ Writes one sample into the folder and returns its path """
    path = os.path.join(folder, name + '.pdf')
    with open(path, 'wb') as sample_file:
        sample_file.write(SAMPLES[name]())
    return path


def main():
    folder = sys.argv[1]
    os.makedirs(folder, exist_ok=True)
    for name in SAMPLES:
        path = write(name, folder)
        print(os.path.basename(path), os.path.getsize(path), 'bytes')


if __name__ == '__main__':
    main()
