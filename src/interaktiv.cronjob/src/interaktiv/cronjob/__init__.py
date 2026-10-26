from typing import NoReturn

import argparse
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.Portal import PloneSite
# noinspection PyUnresolvedReferences
from zope.site.hooks import setSite


class BaseCronjob(object):
    """
       Example usage:
        ./bin/instance run scripts/cronjobs/[FILENAME].py --protocol <PROTOCOL> --host <HOST>
    """

    def __init__(self, app) -> NoReturn:
        args, unknown_args = self._get_args()

        site = app.unrestrictedTraverse(args.site_id)
        setSite(site)

        self.app = app
        self.portal = self.setup_vhm(args.protocol, args.host, args.site_id)
        self.request = self.portal.REQUEST

    def __call__(self) -> NoReturn:
        self.run()
        self.save()

    @staticmethod
    def _get_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('--protocol', required=True)
        parser.add_argument('--host', required=True)
        parser.add_argument('--site_id', default='site')
        return parser.parse_known_args()

    def setup_vhm(self, protocol, host, site_id) -> PloneSite:
        virtual_path = f"/VirtualHostBase/{protocol}/{host}/{site_id}/VirtualHostRoot/{site_id}"
        traversed = self.app.REQUEST.traverse(virtual_path)
        return traversed.context

    def run(self) -> NoReturn:
        """ Custom cronjob process """
        pass

    def save(self) -> NoReturn:
        # Use Zope application server user database (not plone site)
        # noinspection PyUnresolvedReferences
        admin = self.app.acl_users.getUserById('admin')
        newSecurityManager(None, admin)

        # If you make changes to the ZODB, you'll need to commit them manually
        transaction.commit()

        # Perform ZEO client synchronization (if running in clustered mode)
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        self.app._p_jar.sync()
