import plone.api as api
from Acquisition import aq_inner, aq_base
from plone.app.iterate.dexterity.interfaces import IDexterityIterateAware
from zc.relation.interfaces import ICatalog
# noinspection PyUnresolvedReferences
from zope import component

try:
    from zope.intid.interfaces import IIntIds
except ImportError:
    # noinspection PyUnresolvedReferences
    from zope.app.intid.interfaces import IIntIds

WORKINCOPY_RELATIONS = [
    'iterate_working_copy',
    'iterate-working-copy',
]


def get_relations(context):
    if not IDexterityIterateAware.providedBy(context):
        return list()
    context = aq_inner(context)
    # get id
    intids = component.getUtility(IIntIds)
    context_id = intids.queryId(aq_base(context))
    if not context_id:
        # for objects without intid or
        # objects being deleted in the current transaction return empty list
        return list()
    # ask catalog
    catalog = component.getUtility(ICatalog)
    relations = list(catalog.findRelations({'to_id': context_id}))
    relations += list(catalog.findRelations({'from_id': context_id}))
    relations = filter(
        lambda r: r.from_attribute in WORKINCOPY_RELATIONS, relations
    )
    return [relation for relation in relations
            if (relation.from_object and relation.to_object)]


def get_checkout_relation(context):
    relations = get_relations(context)

    if len(relations) > 0:
        return relations[0]
    return None


def get_original(context):
    relation = get_checkout_relation(context)
    if relation and relation.from_id:
        intids = component.getUtility(IIntIds)
        return intids.getObject(relation.from_id)
    return None


def get_working_copy(context):
    relation = get_checkout_relation(context)
    if relation and relation.to_id:
        intids = component.getUtility(IIntIds)
        return intids.getObject(relation.to_id)
    return None


def get_workflow_id(context):
    wf_tool = api.portal.get_tool('portal_workflow')
    return wf_tool.getChainFor(context.portal_type)[0]
