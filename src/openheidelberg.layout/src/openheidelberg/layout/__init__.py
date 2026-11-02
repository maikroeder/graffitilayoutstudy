import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("openheidelberg.layout")
logger = logging.getLogger('openheidelberg.layout')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
