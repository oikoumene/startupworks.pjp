from plone.supermodel import model
from zope import schema
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone import api
from plone.dexterity.content import Item
from Products.CMFPlone.utils import _createObjectByType
from zope.app.intid.interfaces import IIntIds
from zope import component
from z3c.relationfield import RelationValue
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from startupworks.pjp import utils


class ISound(model.Schema, utils.IUserMixin, utils.IVotingMixin):

    title = schema.TextLine(
        title=u'Sound name',
        required=True,
    )

    description = schema.Text(
        title=u'Sound description',
        required=True,
    )

    soundcloud_id = schema.TextLine(
        title=u'Soundcloud ID',
        required=True,
    )

    sound_in_step = RelationList(
        title=u'In pilgrimage steps',
        description=u'Select pilgrimage steps where this sound will appear.',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )

    featured_sound_in_step = RelationList(
        title=u'As featured in pilgrimage steps',
        description=u'Select pilgrimage steps where this sound will appear as a featured resource.',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )


class Sound(Item, utils.VotingMixin, utils.IsPublishedMixin):

    @staticmethod
    def create(title=None, description=None, soundcloud_id=None, step=None):
        folder = utils.get_folder_unrestricted('resources/sounds')
        id = utils.create_id('sound')
        item = _createObjectByType('sound', folder, id)

        item.title = title
        item.description = description
        item.soundcloud_id = soundcloud_id
        item.wcc_user = False

        intids = component.getUtility(IIntIds)
        step_id = intids.getId(step)
        item.sound_in_step = [RelationValue(step_id)]
        notify(ObjectModifiedEvent(item))

        return item

    @staticmethod
    def objects(pilgrimage_step=None, published=None, featured=None):
        if pilgrimage_step is None:
            raise NotImplementedError()
        if published is False:
            raise NotImplementedError()

        objects = utils.back_references(pilgrimage_step, 'sound_in_step')
        objects = utils.back_references(
            pilgrimage_step,
            'sound_in_step' if not featured else 'featured_sound_in_step'
        )
        objects = utils.order_by_drag_n_drop(objects)

        if published is None or published is True:
            objects = filter(lambda x: x.is_published(), objects)

        return objects

    def soundcloud_url_embedded(self):
        return 'https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/{soundcloud_id}' \
               '&amp;color=ff5500&amp;auto_play=false&amp;hide_related=false&amp;show_comments=false&amp;' \
               'show_user=false&amp;show_reposts=false'.format(
            soundcloud_id=self.soundcloud_id
        )

    def soundcloud_url_frame(self):
        return 'https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/{soundcloud_id}' \
               '&amp;auto_play=false&amp;hide_related=false&amp;show_comments=true&amp;show_user=true&amp;' \
               'show_reposts=false&amp;visual=true'.format(
            soundcloud_id=self.soundcloud_id
        )
