import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("openheidelberg.theme")
logger = logging.getLogger('openheidelberg.theme')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
