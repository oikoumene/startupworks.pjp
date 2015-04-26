import json

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import plone.api

from startupworks.pjp.browser import views
from startupworks.pjp import utils, scheme


class ApiView(BrowserView):

    def _response(self, response={}, status_code=200, status_message=''):
        view_response = self.request.response
        view_response.setHeader('Content-type', 'application/json')
        view_response.setStatus(status_code, status_message)
        view_response.setBody(json.dumps(response), lock=True)

        return view_response


class ApiUpvoteView(ApiView):

    def __call__(self):
        id = self.request.form.get('id')
        if not id:
            return self._response(status_code=400)

        obj = plone.api.content.get(UID=id)
        if not obj:
            return self._response(status_code=400)

        obj.upvote()

        return self._response()


class ApiResourcesPaginate(ApiView):

    def __call__(self):
        page = self.request.form.get('page')
        if not page:
            return self._response(status_code=400)
        try:
            self.page = int(page)
        except ValueError:
            return self._response(status_code=400)

        id = self.request.form.get('id')
        if not id:
            return self._response(status_code=400)
        self.obj = plone.api.content.get(UID=id)
        if not self.obj:
            return self._response(status_code=400)

        self.prepare_context()

        return self._response(
            response={
                'html': self.template(),
                'next_page': self.next_page,
            }
        )

    def prepare_context(self):
        raise NotImplementedError()


class ApiCommentsPaginate(ApiResourcesPaginate, views.CommentsMixin):
    template = ViewPageTemplateFile('templates/parts/comments.pt')

    def prepare_context(self):
        self.comments_paginated = self.comments_paginated(start=self.page, step=self.obj)
        self.next_page = self.comments_next_page(start=self.page, step=self.obj)


class ApiVideosPaginate(ApiResourcesPaginate, views.ResourcesVideosMixin):
    template = ViewPageTemplateFile('templates/parts/resources_videos.pt')

    def prepare_context(self):
        self.videos_paginated = self.videos_paginated(start=self.page, step=self.obj)
        self.next_page = self.videos_next_page(start=self.page, step=self.obj)


class ApiSoundsPaginate(ApiResourcesPaginate, views.ResourcesSoundsMixin):
    template = ViewPageTemplateFile('templates/parts/resources_sounds.pt')

    def prepare_context(self):
        self.sounds_paginated = self.sounds_paginated(start=self.page, step=self.obj)
        self.next_page = self.sounds_next_page(start=self.page, step=self.obj)


class ApiDocumentsPaginate(ApiResourcesPaginate, views.ResourcesDocumentsMixin):
    template = ViewPageTemplateFile('templates/parts/resources_documents.pt')

    def prepare_context(self):
        self.documents_paginated = self.documents_paginated(start=self.page, step=self.obj)
        self.next_page = self.documents_next_page(start=self.page, step=self.obj)


class ApiResourcesAdd(ApiView):

    def __call__(self):
        id = self.request.form.get('id')
        if not id:
            return self._response(status_code=400, response={'mssg': 'Forbidden.'})
        obj = plone.api.content.get(UID=id)
        if not obj:
            return self._response(status_code=400, response={'mssg': 'Forbidden.'})

        name = self.request.form.get('name')
        if not utils.Validation.not_empty(name):
            return self._response(status_code=400, response={'mssg': 'No name provided.'})

        email = self.request.form.get('email')
        if utils.Validation.not_empty(email) and not utils.Validation.valid_email(email):
            return self._response(status_code=400, response={'mssg': 'E-mail is not valid.'})

        church = self.request.form.get('church')

        message = self.request.form.get('message')
        if not utils.Validation.not_empty(message):
            return self._response(status_code=400, response={'mssg': 'No message provided.'})

        video_valid, sound_valid, document_valid = False, False, False

        video = self.request.form.get('video')
        if utils.Validation.not_empty(video):
            if not utils.Validation.valid_yt_url(video):
                return self._response(status_code=400, response={'mssg': 'Youtube link is not valid.'})
            else:
                video_valid = True

        sound = self.request.form.get('sound')
        if utils.Validation.not_empty(sound):
            if not utils.Validation.valid_soundcloud_id(sound):
                return self._response(status_code=400, response={
                    'mssg': "Please specify the Soundcloud track ID. If you don't know where "
                            "to find it, please put 0 in the Audio field and include the URL "
                            "of the sound file in the Message field."
                })
            else:
                sound_valid = True

        doc_name = self.request.form.get('docName')
        doc_data = self.request.form.get('docData')
        if doc_name is not None and doc_data is not None:
            if (not utils.Validation.not_empty(doc_name)) or (not utils.Validation.not_empty(doc_data)):
                return self._response(status_code=400, response={'mssg': 'Error while uploading your attachement.'})
            else:
                document_valid = True

        if not any([video_valid, sound_valid, document_valid]):
            return self._response(status_code=400, response={'mssg': 'At least one resource is required.'})

        scheme.resource_upload.ResourceUpload.create(
            name=name, email=email, church=church, message=message,
            video=video if video_valid else None,
            sound=sound if sound_valid else None,
            doc_name=doc_name if document_valid else None,
            doc_data=doc_data if document_valid else None,
            step=obj,
        )

        return self._response(response={
            'mssg': 'Thank you for your contribution! It will appear on the website '
                    'after it has been approved by one of our staff members.'
        })


class ApiCommentsAdd(ApiView):

    def __call__(self):
        id = self.request.form.get('id')
        if not id:
            return self._response(status_code=400, response={'mssg': 'Forbidden.'})
        obj = plone.api.content.get(UID=id)
        if not obj:
            return self._response(status_code=400, response={'mssg': 'Forbidden.'})

        name = self.request.form.get('name')
        if not utils.Validation.not_empty(name):
            return self._response(status_code=400, response={'mssg': 'No name provided.'})

        email = self.request.form.get('email')
        if utils.Validation.not_empty(email) and not utils.Validation.valid_email(email):
            return self._response(status_code=400, response={'mssg': 'E-mail is not valid.'})

        message = self.request.form.get('message')
        if not utils.Validation.not_empty(message):
            return self._response(status_code=400, response={'mssg': 'No message provided.'})

        image_name = self.request.form.get('imageName')
        image_data = self.request.form.get('imageData')
        if (not utils.Validation.not_empty(image_name)) or (not utils.Validation.not_empty(image_data)):
            # return self._response(status_code=400, response={'mssg': 'No photo attached.'})
            image_valid = False
        else:
            image_valid = True

        scheme.user_comment.UserComment.create(
            name=name, email=email, message=message,
            image_name=image_name if image_valid else None,
            image_data=image_data if image_valid else None,
            step=obj,
        )

        return self._response(response={
            'mssg': 'Thank you for your contribution! It will appear on the website '
                    'after it has been approved by one of our staff members.'
        })