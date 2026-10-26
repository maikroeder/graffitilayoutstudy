import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("graffiti.contenttypes")
logger = logging.getLogger('graffiti.contenttypes')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
