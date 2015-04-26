import re
import base64
import time
import hashlib

from plone import api
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from OFS.interfaces import IOrderedContainer
from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zope import schema
from zc.relation.interfaces import ICatalog
from zope.component.hooks import getSite


class IVotingMixin(model.Schema):

    votes_count = schema.Int(
        title=u'Current votes count',
        required=False,
        default=0
    )


class IUserMixin(model.Schema):

    wcc_user = schema.Bool(
        title=u'WCC is an owner',
        required=True,
        default=True
    )


class VotingMixin(object):

    def upvote(self):
        self.votes_count += 1


class IsPublishedMixin(object):

    def is_published(self):
        portal = api.portal.get()
        state = api.content.get_state(obj=self)

        return state == 'published'


class Validation(object):

    @staticmethod
    def valid_email(email):
        try:
            return bool(re.match(r'[^@]+@[^@]+\.[^@]+', email))
        except:
            return False

    @staticmethod
    def not_empty(txt):
        try:
            return True if len(txt.strip()) > 0 else False
        except:
            return False

    @staticmethod
    def valid_yt_url(url):
        if not Validation.not_empty(url):
            return False
        try:
            return bool(re.match(
                r'^(?:https?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$',
                url
            ))
        except:
            return False

    @staticmethod
    def valid_soundcloud_id(id):
        if not Validation.not_empty(id):
            return False
        try:
            int(id)
            return True
        except:
            return False


def get_uid(obj):
    return IUUID(obj, None)


def back_references(source_object, attribute_name):
    # Reference: http://docs.plone.org/external/plone.app.dexterity/docs/advanced/references.html#back-references

    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    result = []
    for rel in catalog.findRelations(
            dict(to_id=intids.getId(aq_inner(source_object)),
            from_attribute=attribute_name)):
        obj = intids.queryObject(rel.from_id)
        if obj is not None and checkPermission('zope2.View', obj):
            result.append(obj)
    return result


def order_by_drag_n_drop(objects):
    # Reference: http://docs.plone.org/develop/plone/content/listing.html#enforcing-manual-sort-order

    def _get_position_in_parent(obj):
        # Use IOrderedContainer interface to extract the object's manual ordering position
        parent = obj.aq_inner.aq_parent
        ordered = IOrderedContainer(parent, None)
        if ordered is not None:
            return ordered.getObjectPosition(obj.getId())
        return 0

    def _sort_by_position(a, b):
        # Python list sorter cmp() using position in parent.
        return _get_position_in_parent(a) - _get_position_in_parent(b)

    return sorted(objects, _sort_by_position)


def base64decode(data):
    return base64.b64decode(data.split(';base64,')[1])


def get_folder_unrestricted(id):
    catalog = getSite().portal_catalog
    site_id = catalog.getPhysicalPath()[1]
    folders = catalog.unrestrictedSearchResults(path='/' + site_id + '/' + id, portal_type='Folder')
    folder = folders[0]._unrestrictedGetObject()

    return folder


def create_id(content_type):
    h = hashlib.new('ripemd160')
    tmp_id = content_type + '-' + str(time.time()).replace('.', '')
    h.update(tmp_id)
    tmp_id = content_type[0] + h.hexdigest() + tmp_id[-3:]

    return tmp_id