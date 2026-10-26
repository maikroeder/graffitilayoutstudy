# -*- coding: utf-8 -*-
from Acquisition import aq_base
from interaktiv.framework import locking
from plone.app.iterate.dexterity import ITERATE_RELATION_NAME
from plone.locking.interfaces import STEALABLE_LOCK
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


# noinspection PyUnusedLocal
def cleanup_after_deleting_workingcopy(workingcopy, event):
    intids = getUtility(IIntIds)
    catalog = getUtility(ICatalog)
    relations = list(catalog.findRelations({
        'to_id': intids.queryId(aq_base(workingcopy)),
        'from_attribute': ITERATE_RELATION_NAME
    }))
    if relations:
        for relation in relations:

            original = relation.from_object
            if not original:
                continue

            # unlock original
            locking.force_unlock(context=original, lock_type=STEALABLE_LOCK)
