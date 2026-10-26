""" Check the PDF files that were uploaded before graffiti.pdfcheck was installed, or check all of them again.

Uses the settings of the PDF check: its content types, checks and limits. Files that did not change since their last
check are skipped, unless --force is given.

Usage:
    bin/instance run scripts/check_pdf_files.py --protocol https --host www.example.org [--site_id site]
        [--path /site/folder] [--force] [--commit-every 50]

The instance must be stopped, or the script runs on a ZEO client of its own.
"""
import argparse
import sys
import traceback

import transaction
from ZODB.POSException import ConflictError
from graffiti.pdfcheck.api import check_object
from graffiti.pdfcheck.settings import get_settings
from interaktiv.cronjob import BaseCronjob


class CheckPdfFiles(BaseCronjob):

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--path', help='only below this path, for example /site/folder')
        parser.add_argument('--force', action='store_true', help='check unchanged files again')
        parser.add_argument('--commit-every', type=int, default=50, help='save after this many checked files')
        arguments, _ = parser.parse_known_args()

        settings = get_settings()
        if not settings:
            sys.exit('graffiti.pdfcheck is not installed in this site')
        query = {'portal_type': settings['portal_types']}
        if arguments.path:
            query['path'] = arguments.path
        # check also when the check on upload is switched off
        settings = dict(settings, enabled=True)
        brains = self.portal.portal_catalog.unrestrictedSearchResults(**query)
        counts = {'checked': 0, 'suitable': 0, 'findings': 0, 'not checked': 0, 'skipped': 0, 'errors': 0}
        for number, brain in enumerate(brains, 1):
            try:
                obj = brain._unrestrictedGetObject()
                result = check_object(obj, force=arguments.force, settings=settings)
            except ConflictError:
                raise
            except Exception:  # noqa: a missing blob or a stale catalog entry must not stop the run
                counts['errors'] += 1
                print('%s: error, %s' % (brain.getPath(), traceback.format_exc().strip().splitlines()[-1]))
                continue
            if result is None:
                counts['skipped'] += 1
                continue
            counts['checked'] += 1
            counts[{True: 'suitable', False: 'findings', None: 'not checked'}[result['suitable']]] += 1
            print('%s: %s' % (brain.getPath(), ', '.join(result['findings'] + result['hints']) or 'suitable'))
            if counts['checked'] % arguments.commit_every == 0:
                transaction.commit()
                print('saved after %d of %d files' % (number, len(brains)))
        print(', '.join('%s %d' % item for item in counts.items()))


CheckPdfFiles(app)()  # noqa: F821 - provided by "bin/instance run"
