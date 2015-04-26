import datetime

from plone.supermodel import model
from zope import schema
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone import api
from plone.dexterity.content import Item
from Products.CMFPlone.utils import _createObjectByType
from plone.namedfile.field import NamedBlobImage
from plone import namedfile
from zope.app.intid.interfaces import IIntIds
from zope import component
from z3c.relationfield import RelationValue
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from startupworks.pjp import utils


class IUserComment(model.Schema, utils.IVotingMixin):

    title = schema.TextLine(
        title=u'Name',
        required=True,
    )

    email = schema.TextLine(
        title=u'E-mail',
        required=True,
    )

    message = schema.Text(
        title=u'Message',
        required=False,
    )

    datetime_added = schema.Datetime(
        title=u'Datetime added',
        required=True,
    )

    image = NamedBlobImage(
        title=u'Image',
        required=False,
    )

    comment_in_steps = RelationList(
        title=u'Pilgrimage step',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )


class UserComment(Item, utils.VotingMixin, utils.IsPublishedMixin):

    @staticmethod
    def create(name=None, email=None, message=None, image_data=None, image_name=None, step=None):
        folder = utils.get_folder_unrestricted('comments')
        id = utils.create_id('comment')
        item = _createObjectByType('user_comment', folder, id)

        item.title = name
        item.email = email
        item.message = message
        item.datetime_added = datetime.datetime.now()
        item.image = namedfile.NamedBlobImage(
            utils.base64decode(image_data),
            filename=image_name.decode('utf-8', 'ignore')
        ) if ((not image_data is None) and (not image_name is None)) else None
        intids = component.getUtility(IIntIds)
        step_id = intids.getId(step)
        item.comment_in_steps = [RelationValue(step_id)]
        notify(ObjectModifiedEvent(item))

        return item

    @staticmethod
    def objects(pilgrimage_step=None, published=None):
        if pilgrimage_step is None:
            raise NotImplementedError()
        if published is False:
            raise NotImplementedError()

        objects = utils.back_references(pilgrimage_step, 'comment_in_steps')
        objects = sorted(objects, key=lambda x: x.datetime_added, reverse=True)

        if published is None or published is True:
            objects = filter(lambda x: x.is_published(), objects)

        return objects

    def display_image_url(self):
        if not self.image:
            return None
        return self.absolute_url() + '/@@display-file/image'
