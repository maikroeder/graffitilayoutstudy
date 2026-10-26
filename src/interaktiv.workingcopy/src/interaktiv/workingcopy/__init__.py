import logging

from interaktiv.workingcopy.utilities.workingcopy import get_checkout_relation
from interaktiv.workingcopy.utilities.workingcopy import get_original
from interaktiv.workingcopy.utilities.workingcopy import get_relations
from interaktiv.workingcopy.utilities.workingcopy import get_working_copy
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("interaktiv.workingcopy")
logger = logging.getLogger('interaktiv.workingcopy')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
