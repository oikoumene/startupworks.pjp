from plone.supermodel import model
from zope import schema
from plone.dexterity.content import Item
from plone.namedfile.field import NamedBlobFile
from plone import api


class IMenuStaticFile(model.Schema):

    title = schema.TextLine(
        title=u'Document name',
        required=True,
    )

    file = NamedBlobFile(
        title=u'File',
        required=True,
    )


class MenuStaticFile(Item):

    @staticmethod
    def objects():
        portal_catalog = api.portal.get_tool('portal_catalog')
        objects = portal_catalog(portal_type='menu_static_file')
        objects = [brain.getObject() for brain in objects]

        return objects

    def download_url(self):
        return self.absolute_url() + '/@@download/file'