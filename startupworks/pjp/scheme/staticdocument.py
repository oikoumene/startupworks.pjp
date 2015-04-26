import tempfile
import os
import subprocess
from plone.supermodel import model
from zope import schema
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.dexterity.content import Item
from plone.namedfile.field import NamedBlobFile
from plone import api
from Products.CMFPlone.utils import _createObjectByType
from plone import namedfile
from zope.app.intid.interfaces import IIntIds
from zope import component
from z3c.relationfield import RelationValue
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from startupworks.pjp import utils


class IStaticDocument(model.Schema, utils.IUserMixin, utils.IVotingMixin):

    title = schema.TextLine(
        title=u'Document name',
        required=True,
    )

    description = schema.Text(
        title=u'Document description',
        required=True,
    )

    file = NamedBlobFile(
        title=u'File',
        required=True,
    )

    file_thumb = NamedBlobFile(
        title=u'File thumb',
        description=u'Thumbnail of the file (if PDF) - will be generated automatically.',
        required=False,
    )

    doc_in_step = RelationList(
        title=u'In pilgrimage steps',
        description=u'Select pilgrimage steps where this document will appear.',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )

    featured_doc_in_step = RelationList(
        title=u'As featured in pilgrimage steps',
        description=u'Select pilgrimage steps where this document will appear as a featured resource.',
        default=[],
        value_type=RelationChoice(
            source=ObjPathSourceBinder(
                path={'query': '/en/pilgrimage-steps'},
            ),
        ),
        required=False,
    )


class StaticDocument(Item, utils.VotingMixin, utils.IsPublishedMixin):

    @staticmethod
    def create(title=None, description=None, doc_data=None, doc_name=None, step=None):
        folder = utils.get_folder_unrestricted('resources/documents')
        id = utils.create_id('staticdocument')
        item = _createObjectByType('staticdocument', folder, id)

        item.title = title
        item.description = description
        item.file = namedfile.NamedBlobFile(
            utils.base64decode(doc_data),
            filename=doc_name.decode('utf-8', 'ignore')
        )
        item.wcc_user = False

        intids = component.getUtility(IIntIds)
        step_id = intids.getId(step)
        item.doc_in_step = [RelationValue(step_id)]
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
            'doc_in_step' if not featured else 'featured_doc_in_step'
        )
        objects = utils.order_by_drag_n_drop(objects)

        if published is None or published is True:
            objects = filter(lambda x: x.is_published(), objects)

        return objects

    @staticmethod
    def create_thumb(item):
        if not item.file:
            return

        if item.file.contentType != 'application/pdf':
            if item.file_thumb is not None:
                item.file_thumb = None
            return

        source = item.file.open()
        (fd, filename) = tempfile.mkstemp()
        dest_filename = filename + '.png'

        try:
            tmp_source = os.fdopen(fd, 'wb')
            tmp_source.write(source.read())
            tmp_source.close()

            command = "convert -quality 95 -thumbnail '307x' -crop '307x168+0+0' +repage {source}[0] {output}".format(
                source=filename,
                output=dest_filename
            )
            proc = subprocess.Popen(command, shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            proc.communicate()[0]

            tmp_dest = open(dest_filename, 'rb')

            item.file_thumb = namedfile.NamedBlobFile(
                tmp_dest.read(),
                filename=os.path.basename(dest_filename.decode('utf-8', 'ignore'))
            )
            tmp_dest.close()
        except:
            pass
        finally:
            try:
                os.remove(filename)
                os.remove(dest_filename)
            except:
                pass

    def download_url(self):
        return self.absolute_url() + '/@@download/file'

    def display_thumb_url(self):
        if not self.file_thumb:
            return None
        return self.absolute_url() + '/@@display-file/file_thumb'


def on_object_modified(staticdocument, event):
    StaticDocument.create_thumb(staticdocument)


def on_object_added(staticdocument, event):
    StaticDocument.create_thumb(staticdocument)
