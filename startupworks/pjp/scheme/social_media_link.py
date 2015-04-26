from plone.supermodel import model
from zope import schema
from plone.dexterity.content import Item
from plone.namedfile.field import NamedBlobFile
from plone import api


class ISocialMediaLink(model.Schema):

    title = schema.TextLine(
        title=u'Document name',
        required=True,
    )

    url = schema.TextLine(
        title=u'URL',
        required=True,
    )

    icon = schema.TextLine(
        title=u'Icon class',
        required=True,
    )


class SocialMediaLink(Item):

    @staticmethod
    def objects():
        portal_catalog = api.portal.get_tool('portal_catalog')
        objects = portal_catalog(portal_type='social_media_link')
        objects = [brain.getObject() for brain in objects]

        return objects
