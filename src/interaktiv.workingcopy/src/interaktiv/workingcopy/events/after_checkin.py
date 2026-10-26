from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implementer


class IAfterCheckinEvent(IObjectEvent):
    """ """


@implementer(IAfterCheckinEvent)
class AfterCheckinEvent(ObjectEvent):

    def __init__(self, original):
        ObjectEvent.__init__(self, original)
