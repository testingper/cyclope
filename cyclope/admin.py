#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2010-2013 Código Sur Sociedad Civil.
# All rights reserved.
#
# This file is part of Cyclope.
#
# Cyclope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cyclope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
admin
-----
configuration for the Django admin
"""

from django.db import models
from django.contrib import admin
from django.core import urlresolvers

from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
import django.forms
from django.contrib.auth import load_backend

from mptt_tree_editor.admin import TreeEditor

from cyclope.models import *
from cyclope.forms import (MenuItemAdminForm, SiteSettingsAdminForm,
                            LayoutAdminForm, RegionViewInlineForm,
                            RelatedContentForm, AuthorAdminForm,
                            DesignSettingsAdminForm)

from cyclope.widgets import get_default_text_widget
from cyclope.core.collections.admin import CollectibleAdmin
from cyclope.core.collections.models import Category
import cyclope.settings as cyc_settings
from cyclope.utils import PermanentFilterMixin
from cyclope.signals import admin_post_create
from cyclope.core.collections.admin import CollectibleAdmin


# Set default widget for all admin textareas
default_admin_textfield = FORMFIELD_FOR_DBFIELD_DEFAULTS[models.TextField]
default_admin_textfield['widget'] = get_default_text_widget()

class RelatedContentInline(generic.GenericStackedInline):
    form = RelatedContentForm
    ct_field = 'self_type'
    ct_fk_field = 'self_id'
    model = RelatedContent
    extra = 0


class BaseContentAdmin(admin.ModelAdmin):
    """Base class for content models to use instead of admin.ModelAdmin
    """
    inlines = [RelatedContentInline]
    date_hierarchy = 'creation_date'

    class Media:
        js = (cyc_settings.CYCLOPE_JQUERY_PATH,)

    def response_change(self, request, obj):
        if '_frontend' in request.REQUEST:
            return HttpResponseRedirect(obj.get_absolute_url())
        return super(BaseContentAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        admin_post_create.send(sender=obj.__class__, request=request, instance=obj)
        if '_frontend' in request.REQUEST:
            return HttpResponseRedirect(obj.get_absolute_url())
        return super(BaseContentAdmin, self).response_add(request, obj, post_url_continue)

    def has_delete_permission(self, request, obj=None):
        # this is redundant with _popup, which already sets delete_permission to False
        if '_frontend' in request.REQUEST:
            return False
        return super(BaseContentAdmin, self).has_delete_permission(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if '_frontend' in request.REQUEST:
            if extra_context is None:
                extra_context = {}
            extra_context['frontend_admin'] = 'frontend_admin'

        return super(BaseContentAdmin, self).change_view(request, object_id,
                                                          form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        cat_perm_backend = load_backend('cyclope.core.perms.backends.CategoryPermBackend')
        response = super(BaseContentAdmin, self).changelist_view(request, extra_context)
        u = request.user
        # row based perms.
        # only return content objects for which user is granted edit perms
        if not (u.is_authenticated() and (u.is_superuser or
           u.is_staff and u.has_perm('collections.change_category'))):
            cl = response.context_data["cl"]
            query_set = cl.query_set._clone()
            forbidden = []
            for content_object in query_set:
                if not cat_perm_backend.has_perm(u, "edit_content", content_object):
                    forbidden.append(content_object.pk)
            ## TODO(nicoechaniz): there might be a way to achieve this without repeating this steps from ChangeList view. Investigate and refactor if possible.
            new_query_set = query_set.exclude(id__in=forbidden)
            cl.query_set = new_query_set
            cl.get_results(request)
            response.context_data["cl"] = cl

        return response

    def add_view(self, request, form_url='', extra_context=None):
        if '_frontend' in request.REQUEST:
            if extra_context is None:
                extra_context = {}
            extra_context['frontend_admin'] = 'frontend_admin'
        if '_from_category' in request.REQUEST:
            category_slug = request.REQUEST['_from_category']
            if category_slug:
                category = Category.objects.get(slug=category_slug)
                extra_context['initial_category'] = category.id
                extra_context['initial_collection'] = category.collection.id
        return super(BaseContentAdmin, self).add_view(request, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        # sets the user as the creator of the content
        if getattr(obj, 'user', None) is None:
            obj.user = request.user
        obj.save()


class MenuItemAdmin(TreeEditor, PermanentFilterMixin):
    form = MenuItemAdminForm
    fieldsets = ((None,
                  {'fields': ('menu', 'parent', 'name', 'slug', 'site_home', 'active')}),
                 (_('content details'),
                  {'fields':('custom_url', 'content_type', 'content_view',
                             'view_options', 'content_object',),
                  'description': _(u"Either set an URL here or select a content"
                                    "type and view.")
                  }),
                 (_('layout'),
                  {'fields':('layout', 'persistent_layout'),
                   'classes': ('collapse',),
                   'description': _(u"Set the layout that will be used when this "
                                    "menuitem is selected.")
                   }),
                )
    list_filter = ('menu',)

    permanent_filters = (
        (u"menu__id__exact",
         lambda request: unicode(Menu.objects.all()[0].id)),
    )

    class Media:
        js = ( cyc_settings.CYCLOPE_JQUERY_PATH,)

    def changelist_view(self, request, extra_context=None):
        self.do_permanent_filters(request)
        return super(MenuItemAdmin, self).changelist_view(request, extra_context)

admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Menu)

class RegionViewInline(admin.StackedInline):
    form = RegionViewInlineForm
    model = RegionView
    extra = 1

####################################
from cyclope.models import SiteSettings
from cyclope.themes import get_theme
class LayoutAdmin(admin.ModelAdmin):
    form = LayoutAdminForm
    inlines = (RegionViewInline, )
    exclude = ('image_path',)
    
    # get current Layout's regions ordered by weight
    # overrides change_view TODO(NumericA) django > 1.4  must override get_context_data instead?
    def change_view(self, request, object_id, form_url='', extra_context=None):
        theme_settings = get_theme(SiteSettings.objects.get().theme)
        layout_template = Layout.objects.get(pk=object_id).template
        layout_regions = theme_settings.layout_templates[layout_template]['regions']
        layout_regions = sorted(layout_regions.items(), key=lambda x: x[1]['weight'])
        extra_context = {'layout_regions': layout_regions}
        return super(LayoutAdmin, self).change_view(request, object_id, form_url, extra_context)
        
    class Media:
        js = (cyc_settings.CYCLOPE_JQUERY_PATH,)

admin.site.register(Layout, LayoutAdmin)

class SingletonAdminMixin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """ Prevent addition of new objects """
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def response_change(self, request, obj):
        if not '_continue' in request.POST:
            return HttpResponseRedirect(urlresolvers.reverse('admin:index'))
        else:
            return super(SingletonAdminMixin, self).response_change(request, obj)

DESIGN_FIELDS = (
    'global_title', 'theme', 'default_layout', 'head_image', 'favicon_image',
    'show_head_title', 'body_font', 'body_custom_font', 'titles_font', 
    'titles_custom_font', 'font_size', 'hide_content_icons', 
    'skin_setting',
)
 

class SiteSettingsAdmin(SingletonAdminMixin):
    form = SiteSettingsAdminForm
    exclude = ('site', ) + DESIGN_FIELDS

admin.site.register(SiteSettings, SiteSettingsAdmin)


class DesignSettingsAdmin(SingletonAdminMixin):
    form = DesignSettingsAdminForm

    fieldsets = (
        (_('General'), {
            'fields': ('global_title', 'show_head_title', 'head_image', 'favicon_image', 'theme', 'home_layout', 'default_layout', )
        }),
        (_('Fonts'), {
            'fields': ('font_size', ('body_font', 'body_custom_font'), 
                       ('titles_font', 'titles_custom_font',) )
        }),
        (_('Colours'), {
            'classes': ['colours', ],
            'fields': ('skin_setting',)
        }),
        (_('Other'), {
            'fields': ( 'hide_content_icons', )
        }),
    )

    class Media:
        js = ("js/jscolor/jscolor.js",)

admin.site.register(DesignSettings, DesignSettingsAdmin)


class ImageAdmin(admin.ModelAdmin):
    list_display = ['thumbnail']

admin.site.register(Image, ImageAdmin)

class AuthorAdmin(CollectibleAdmin):
    form = AuthorAdminForm
    list_display = ('name', 'thumbnail')
    search_fields = ('name', 'origin', 'notes')
    inlines = CollectibleAdmin.inlines

admin.site.register(Author, AuthorAdmin)

admin.site.register(Source)

class SiteAdmin(admin.ModelAdmin):
    list_display = ('domain', 'name')
    search_fields = ('domain', 'name')

    def has_add_permission(self, request):
        """ Prevent addition of new objects """
        return False

    def has_delete_permission(self, request, obj=None):
        return False



import django.contrib.sites.admin # Force register of django's SiteAdmin
admin.site.unregister(Site)
admin.site.register(Site, SiteAdmin)
