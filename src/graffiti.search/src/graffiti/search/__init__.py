import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("graffiti.search")
logger = logging.getLogger('graffiti.search')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""