import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory("graffiti.policy")
logger = logging.getLogger('graffiti.policy')


# noinspection PyUnusedLocal
def initialize(context):
    """Initializer called when used as a Zope 2 product."""
