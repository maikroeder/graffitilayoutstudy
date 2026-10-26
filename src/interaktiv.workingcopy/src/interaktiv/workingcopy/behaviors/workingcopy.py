# -*- coding: utf-8 -*-
# noinspection PyProtectedMember
from interaktiv.workingcopy import _
from plone.app.vocabularies.catalog import CatalogSource
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.locking.interfaces import ITTWLockable
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
import zope.schema as schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implementer


class IWorkingcopyBehavior(model.Schema, ITTWLockable):
    """ Behavior gives the ability
        to add additional fields
    """

    model.fieldset(
        'workingcopy',
        label=_(u"Arbeitskopie"),
        fields=[
            'working_copy_version_notice',
            'working_copy_type'
        ]
    )

    directives.omitted('working_copy_version_notice')
    working_copy_version_notice = schema.Text(
        title=u'Arbeitskopie Änderungsnotiz',
        required=False
    )

    directives.omitted('working_copy_type')
    working_copy_type = schema.TextLine(
        title=u'Art der Arbeitskopie',
        required=False
    )


alsoProvides(IWorkingcopyBehavior, IFormFieldProvider)


@implementer(IWorkingcopyBehavior)
class WorkingcopyBehavior(object):
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
