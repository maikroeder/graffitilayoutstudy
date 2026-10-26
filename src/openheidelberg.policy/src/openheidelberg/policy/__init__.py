import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("openheidelberg.policy")
logger = logging.getLogger('openheidelberg.policy')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
