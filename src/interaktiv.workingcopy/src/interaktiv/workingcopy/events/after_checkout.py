from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import Attribute
from zope.interface import implementer
from plone.app.iterate.subscribers.metadata import handleCheckout


class IAfterCheckoutEvent(IObjectEvent):
    """  """

    working_copy = Attribute("The object's working copy")
    relation = Attribute("The Working Copy Archetypes Relation Object")


@implementer(IAfterCheckoutEvent)
class AfterCheckoutEvent(ObjectEvent):

    def __init__(self, original, working_copy, relation):
        ObjectEvent.__init__(self, original)
        self.working_copy = working_copy
        self.relation = relation

        handleCheckout(self)
