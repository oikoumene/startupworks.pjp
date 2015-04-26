import urlparse

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


class IVideo(model.Schema, utils.IUserMixin, utils.IVotingMixin):

    title = schema.TextLine(
        title=u'Video name',
        required=True,
    )

    description = schema.Text(
        title=u'Video description',
        required=True,
    )

    url_youtube = schema.TextLine(
        title=u'Youtube URL',
        required=True,
    )

    video_in_step = RelationList(
        title=u'In pilgrimage steps',
        description=u'Select pilgrimage steps where this video will appear.',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )

    featured_video_in_step = RelationList(
        title=u'As featured in pilgrimage steps',
        description=u'Select pilgrimage steps where this video will appear as a featured resource.',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )


class Video(Item, utils.VotingMixin, utils.IsPublishedMixin):

    @staticmethod
    def create(title=None, description=None, url_youtube=None, step=None):
        folder = utils.get_folder_unrestricted('resources/videos')
        id = utils.create_id('video')
        item = _createObjectByType('video', folder, id)

        item.title = title
        item.description = description
        item.url_youtube = url_youtube
        item.wcc_user = False

        intids = component.getUtility(IIntIds)
        step_id = intids.getId(step)
        item.video_in_step = [RelationValue(step_id)]
        notify(ObjectModifiedEvent(item))

        return item

    @staticmethod
    def objects(pilgrimage_step=None, published=None, featured=None):
        if pilgrimage_step is None:
            raise NotImplementedError()
        if published is False:
            raise NotImplementedError()

        objects = utils.back_references(
            pilgrimage_step,
            'video_in_step' if not featured else 'featured_video_in_step'
        )
        objects = utils.order_by_drag_n_drop(objects)

        if published is None or published is True:
            objects = filter(lambda x: x.is_published(), objects)

        return objects

    def url_youtube_embedded(self):
        return 'http://www.youtube.com/embed/{hash}'.format(hash=self._hash_from_url_youtube())

    def url_youtube_bg_img(self):
        return 'http://img.youtube.com/vi/{hash}/hqdefault.jpg'.format(hash=self._hash_from_url_youtube())

    def _hash_from_url_youtube(self):
        # Reference: http://stackoverflow.com/a/7936523/545435

        query = urlparse.urlparse(self.url_youtube)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        return ''
