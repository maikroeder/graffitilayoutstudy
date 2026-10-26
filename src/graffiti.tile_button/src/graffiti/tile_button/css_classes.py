import re
from typing import List, Optional

from graffiti.tile_button import _
from zope.schema import ValidationError

CSS_CLASS_PATTERN = re.compile(r'^[A-Za-z0-9_-]+$')


class InvalidCssClasses(ValidationError):
    __doc__ = _(
        u'msg_invalid_css_classes',
        default=u'CSS classes may only contain letters, digits, hyphens and underscores, separated by spaces.'
    )


def check_css_classes(value: Optional[str]) -> bool:
    """ Field constraint: every class separated by whitespace must match CSS_CLASS_PATTERN """
    for css_class in (value or '').split():
        if not CSS_CLASS_PATTERN.match(css_class):
            raise InvalidCssClasses(value)
    return True


def split_css_classes(value: Optional[str]) -> List[str]:
    """ The valid classes of a value, invalid ones are dropped (values set without the form) """
    return [css_class for css_class in (value or '').split() if CSS_CLASS_PATTERN.match(css_class)]
