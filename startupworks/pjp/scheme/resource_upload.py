import datetime

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

from startupworks.pjp import scheme, utils


class IResourceUpload(model.Schema):

    name = schema.TextLine(
        title=u'Name',
        required=True,
    )

    email = schema.TextLine(
        title=u'E-mail',
        required=False,
    )

    church = schema.TextLine(
        title=u'Your church',
        required=False,
    )

    message = schema.Text(
        title=u'Message',
        required=True,
    )

    video = RelationList(
        title=u'Video',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/resources/videos'}
            ),
        ),
        required=False
    )

    sound = RelationList(
        title=u'Sound',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/resources/sounds'}
            ),
        ),
        required=False
    )

    document = RelationList(
        title=u'Document',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/resources/documents'}
            ),
        ),
        required=False
    )


class ResourceUpload(Item):

    @staticmethod
    def create(name=None, email=None, church=None, message=None,
               video=None, sound=None, doc_data=None, doc_name=None,
               step=None):
        folder = utils.get_folder_unrestricted('resources/user-resources-uploads')
        id = utils.create_id('resource_upload')
        item = _createObjectByType('resource_upload', folder, id)

        intids = component.getUtility(IIntIds)
        item.title = u'{name} uploaded {count} resource(s) on {date}'.format(
            name=name,
            count=len(filter(lambda x: x, [bool(video), bool(sound), bool(doc_data) and bool(doc_name)])),
            date=datetime.datetime.now().strftime('%A %d. %B %Y, %H:%M')
        )
        item.name = name
        item.email = email
        item.church = church
        item.message = message
        if video is not None:
            video_obj = scheme.video.Video.create(
                title='Video uploaded by {user}'.format(user=name),
                description='',
                url_youtube=video,
                step=step
            )
            video_id = intids.getId(video_obj)
            item.video = [RelationValue(video_id)]
            notify(ObjectModifiedEvent(item))

        if sound is not None:
            sound_obj = scheme.sound.Sound.create(
                title='Sound uploaded by {user}'.format(user=name),
                description='',
                soundcloud_id=sound,
                step=step
            )
            sound_id = intids.getId(sound_obj)
            item.sound = [RelationValue(sound_id)]
            notify(ObjectModifiedEvent(item))

        if doc_data is not None and doc_name is not None:
            doc_obj = scheme.staticdocument.StaticDocument.create(
                title='Document uploaded by {user}'.format(user=name),
                description='',
                doc_data=doc_data,
                doc_name=doc_name,
                step=step
            )
            doc_id = intids.getId(doc_obj)
            item.document = [RelationValue(doc_id)]
            notify(ObjectModifiedEvent(item))

        return item
