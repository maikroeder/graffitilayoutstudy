""" The upload utility of interaktiv.basetiles, without stopping the upload when there is no preview image

interaktiv.basetiles makes a preview image of the first page of a PDF file (behavior "preview image").
Before version 17.0.1 the whole upload fails if that does not work: for a damaged or encrypted file,
or when the program gm is missing. Since 17.0.1 interaktiv.basetiles saves the file without preview image
(commit f8f98233 there). This utility does the same for older versions, and changes nothing for newer ones.
"""
import logging

from interaktiv.basetiles.utilities.upload_file import UploadFileUtility

logger = logging.getLogger(__name__)

# the error of interaktiv.basetiles before 17.0.1, when there is no preview image
PREVIEW_ERROR = 'could not generate PDF Image'


class UploadFileUtilityWithoutPreviewError(UploadFileUtility):

    @staticmethod
    def _get_first_image_of_pdf(pdf_path):
        try:
            return UploadFileUtility._get_first_image_of_pdf(pdf_path)
        except FileNotFoundError:
            # the program gm is missing
            logger.error('No preview image for %s, the program gm is missing', pdf_path)
            return None

    def get_image_blob(self, file_path):
        try:
            return super().get_image_blob(file_path)
        except Exception as error:
            if type(error) is not Exception or str(error) != PREVIEW_ERROR:
                raise
            return None
