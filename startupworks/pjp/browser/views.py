import datetime

from Products.Five.browser import BrowserView
from plone import api

from startupworks.pjp import scheme, utils


class ContextMixin(object):

    def pilgrimage_steps(self):
        return scheme.pilgrimage_step.PilgrimageStep.objects()

    def social_media_links(self):
        return scheme.social_media_link.SocialMediaLink.objects()

    def menu_static_files(self):
        return scheme.menu_static_file.MenuStaticFile.objects()

    def root_api_url(self):
        portal = api.portal.get()
        return portal.absolute_url() + '/'

    def pilgrimage_steps_url(self):
        portal = api.portal.get()
        page = portal['pilgrimage-steps']

        return page.absolute_url()

    def current_year(self):
        return datetime.datetime.now().year


class HomeView(ContextMixin, BrowserView):
    pass


class PilgrimageStepsView(ContextMixin, BrowserView):

    def __call__(self):
        return super(PilgrimageStepsView, self).__call__()

    def show_sidebar_notice(self):
        return True

    def pilgrimage_steps_splitted(self):
        split_after = 2
        steps = self.pilgrimage_steps()
        if len(steps) < split_after + 1:
            return steps

        return steps[split_after:] + steps[:split_after]


class CommentsMixin(object):
    pagination = 3

    def comments_paginated(self, start=0, step=None):
        return self._comments(step=step)[start * self.pagination:(start + 1) * self.pagination]

    def comments_next_page(self, start=0, step=None):
        return start + 1 if self._comments_show_more(start=start + 1, step=step) else ''

    def _comments(self, step=None):
        return scheme.user_comment.UserComment.objects(
            pilgrimage_step=step if step is not None else self.context,
            published=True
        )

    def _comments_show_more(self, start=0, step=None):
        return len(self._comments(step=step)) > start * self.pagination


class PilgrimageStepView(ContextMixin, CommentsMixin, BrowserView):

    def __call__(self):
        return super(PilgrimageStepView, self).__call__()

    def navigation(self):
        steps = self.pilgrimage_steps()

        index = 0
        for step in steps:
            if utils.get_uid(step) == self.UID():
                break
            index += 1

        return {
            'prev_url': False if index == 0 else steps[index - 1].url(),
            'next_url': False if index >= len(steps) - 1 else steps[index + 1].url(),
        }

    def UID(self):
        return utils.get_uid(self.context.aq_base)

    def resources_url(self):
        return self.context.absolute_url() + '/resources'

    def show_sidebar_notice(self):
        return False

    def featured_video(self):
        objects = scheme.video.Video.objects(
            pilgrimage_step=self.context, published=True, featured=True
        )
        return objects[0] if objects else None

    def featured_sound(self):
        objects = scheme.sound.Sound.objects(
            pilgrimage_step=self.context, published=True, featured=True
        )
        return objects[0] if objects else None

    def featured_document(self):
        objects = scheme.staticdocument.StaticDocument.objects(
            pilgrimage_step=self.context, published=True, featured=True
        )
        return objects[0] if objects else None


class ResourcesMixin(object):
    pagination = 3


class ResourcesVideosMixin(ResourcesMixin):

    def videos_paginated(self, start=0, step=None):
        return self._videos(step=step)[start * self.pagination:(start + 1) * self.pagination]

    def videos_next_page(self, start=0, step=None):
        return start + 1 if self._videos_show_more(start=start + 1, step=step) else ''

    def _videos(self, step=None):
        return scheme.video.Video.objects(
            pilgrimage_step=step if step is not None else self.context,
            published=True
        )

    def _videos_show_more(self, start=0, step=None):
        return len(self._videos(step=step)) > start * self.pagination


class ResourcesSoundsMixin(ResourcesMixin):

    def sounds_paginated(self, start=0, step=None):
        return self._sounds(step=step)[start * self.pagination:(start + 1) * self.pagination]

    def sounds_next_page(self, start=0, step=None):
        return start + 1 if self._sounds_show_more(start=start + 1, step=step) else ''

    def _sounds(self, step=None):
        return scheme.sound.Sound.objects(
            pilgrimage_step=step if step is not None else self.context,
            published=True
        )

    def _sounds_show_more(self, start=0, step=None):
        return len(self._sounds(step=step)) > start * self.pagination


class ResourcesDocumentsMixin(ResourcesMixin):

    def documents_paginated(self, start=0, step=None):
        return self._documents(step=step)[start * self.pagination:(start + 1) * self.pagination]

    def documents_next_page(self, start=0, step=None):
        return start + 1 if self._documents_show_more(start=start + 1, step=step) else ''

    def _documents(self, step=None):
        return scheme.staticdocument.StaticDocument.objects(
            pilgrimage_step=step if step is not None else self.context,
            published=True
        )

    def _documents_show_more(self, start=0, step=None):
        return len(self._documents(step=step)) > start * self.pagination



class PilgrimageStepResourcesView(ResourcesVideosMixin, ResourcesSoundsMixin,
                                  ResourcesDocumentsMixin, PilgrimageStepView):
    pass
