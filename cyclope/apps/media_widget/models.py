from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.forms.widgets import MultipleHiddenInput
from django.forms import fields
from django.forms import ModelMultipleChoiceField

from cyclope.apps.medialibrary.models import Picture
from django.utils.safestring import mark_safe
from django.utils.html import escape


class MediaWidget(MultipleHiddenInput):
    def __init__(self, attrs=None):
        super(MediaWidget, self).__init__(attrs)
        
    def render(self, name, value, attrs=None):
        inputs = super(MediaWidget, self).render(name, value, attrs)# <input id="id_pictures_0" type="hidden" name="pictures">
        string = _('Manage pictures')
        button = u'<button id="media_widget_button" type="button">%s</button>\n' % string
        thumbs = u''
        for pic_id in value:
            thumbs += Picture.objects.get(pk=pic_id).thumbnail()+'&nbsp;\n'
        widget = u'<div id="media_widget">'+ button + u'<span id="media_widget_pictures">' + inputs + thumbs + u'</span></div>'
        widget = mark_safe(widget)
        return widget

class MediaWidgetField(ModelMultipleChoiceField):
    """
    Just inheriting:
    - unpacks multiple hidden inputs as pictures list
    - validates that all ids belong to Pictures.
    """
    pass
