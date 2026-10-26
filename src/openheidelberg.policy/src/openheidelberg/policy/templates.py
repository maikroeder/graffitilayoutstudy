import io

from PIL import Image
from PIL import ImageDraw
from interaktiv.basetiles.utilities.templates import TemplatesUtility
from openheidelberg.policy import logger
from plone.namedfile.file import NamedBlobImage

WIDTH = 400
HEIGHT = 300
BACKGROUND = (238, 238, 238)
BORDER = (170, 170, 170)
TEXT = (90, 90, 90)


class PlaceholderTemplatesUtility(TemplatesUtility):
    """ Templates utility that never starts a browser.

    interaktiv.basetiles renders the thumbnail of a template with puppeteer (headless
    Chrome). Here get_thumbnail returns a neutral placeholder image instead; the template
    picker then shows a grey box rather than a screenshot.
    """

    @staticmethod
    def get_thumbnail(url: str, user: str, password: str) -> NamedBlobImage:
        logger.info('Using placeholder thumbnail instead of rendering %s', url)
        image = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND)
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=BORDER)
        draw.text((WIDTH // 2 - 30, HEIGHT // 2 - 5), 'Template', fill=TEXT)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return NamedBlobImage(data=buffer.getvalue(), filename='thumbnail.png')
