from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implementer


class IAfterCancelEvent(IObjectEvent):
    """ """


@implementer(IAfterCancelEvent)
class AfterCancelEvent(ObjectEvent):

    def __init__(self, original):
        ObjectEvent.__init__(self, original)
