import interaktiv.framework as framework
import plone.api as api


# noinspection PyUnusedLocal
def upgrade(plone_setup):
    brains = api.content.find(context=api.portal.get())
    for brain in brains:
        obj = brain.getObject()
        try:
            lock_info = framework.locking.lock_info(obj)
        except TypeError:
            lock_info = None
        if not lock_info:
            continue
        if lock_info['type'].__name__ == 'workingcopy.lock':
            print(f"Unlocking object.. ({obj.absolute_url()})")
            framework.locking.force_unlock(obj)
