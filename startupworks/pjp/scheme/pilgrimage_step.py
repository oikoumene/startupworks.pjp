from plone.supermodel import model
from zope import schema
from plone.dexterity.content import Item
from plone import api


class IPilgrimageStep(model.Schema):

    title = schema.TextLine(
        title=u'Title',
        required=True,
    )

    teaser = schema.TextLine(
        title=u'Teaser',
        required=True,
    )

    header = schema.TextLine(
        title=u'Header',
        required=True,
    )

    description = schema.Text(
        title=u'Description',
        required=True,
    )

    twitter_widget_id = schema.TextLine(
        title=u'Twitter widget ID',
        required=False,
        description=u'You may generate new twitter widget or edit existing one here: '
                    u'https://twitter.com/settings/widgets'
    )

    instagram_hashtags = schema.TextLine(
        title=u'Instagram hashtags',
        required=False,
        description=u'Please specify hashtags in a comma-separated list, e.g. #pilgrimage, #wcc. '
                    u'If you type @worldcouncilofchurches here, user feed would be displayed instead of '
                    u'hashtags.'
    )

    colour = schema.TextLine(
        title=u'Colour',
        required=True,
    )

    step_number = schema.Int(
        title=u'Step number',
        required=True
    )


class PilgrimageStep(Item):

    MENU_STEPS_CLASSES = {
        1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
        6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'
    }

    @staticmethod
    def objects():
        portal_catalog = api.portal.get_tool('portal_catalog')
        objects = portal_catalog(portal_type='pilgrimage_step')
        objects = [brain.getObject() for brain in objects]
        objects = sorted(objects, key=lambda x: x.step_number)

        return objects

    def url(self):
        return self.absolute_url()

    def step_number_text(self):
        return self.MENU_STEPS_CLASSES[self.step_number]

    def instagram_hashtags_joined(self):
        if not self.instagram_hashtags or '@' in self.instagram_hashtags:
            return u''
        return u','.join(map(
            lambda x: x.strip(),
            self.instagram_hashtags.replace('#', '').split(',')
        ))

    def instagram_user_feed(self):
        if not self.instagram_hashtags or '#' in self.instagram_hashtags:
            return u''
        return self.instagram_hashtags.replace('@', '').strip()
