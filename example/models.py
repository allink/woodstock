# feincms stuff
from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent
from feincms.content.application.models import ApplicationContent

Page.register_templates({
    'key': 'base',
    'title': 'Basic Template',
    'path': 'base.html',
    'regions': (
        ('main', 'Main Region'),
    ),
})

Page.create_content_type(RichTextContent)
Page.create_content_type(ApplicationContent, APPLICATIONS=(
    ('woodstock.urls.simple', 'Woodstock Simple'),
))

# pennyblack stuff
from pennyblack.models import Newsletter
from pennyblack.content.richtext import TextOnlyNewsletterContent, \
    TextWithImageNewsletterContent

Newsletter.register_templates({
    'key': 'base',
    'title': 'Generic Newsletter',
    'path': 'base_newsletter.html',
    'regions': (
        ('main', 'Main Region'),
    ),
})
    
Newsletter.create_content_type(TextOnlyNewsletterContent)
Newsletter.create_content_type(TextWithImageNewsletterContent)
