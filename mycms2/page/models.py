from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import bleach
from bs4 import BeautifulSoup
from django.utils.html import strip_tags

from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from mptt.models import MPTTModel, TreeForeignKey
from mycms2 import settings

@python_2_unicode_compatible
class Theme(models.Model):
    """
    Theme Model
    """
    name = models.CharField(_('name'), max_length=200)
    value = models.CharField(_('value'), max_length=200)
    is_actived = models.BooleanField(_('is actived'), default=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """If it's first theme, set actived"""
        if self.is_actived == True:
            Theme.objects.exclude(pk=self.pk).filter(is_actived=True)\
                    .update(is_actived=False)
        super(Theme, self).save(*args, **kwargs)


    class Meta(object):
        verbose_name = _('theme')
        verbose_name_plural = _('theme')


@python_2_unicode_compatible
class Template(models.Model):
    """
    Template Model
    """
    theme = models.ForeignKey(Theme, related_name='templates',\
            verbose_name=_('theme'))
    name = models.CharField(_('name'), max_length=200)
    code = models.TextField(_('code'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta(object):
        verbose_name = _('template')
        verbose_name_plural = _('template')


@python_2_unicode_compatible
class Page(MPTTModel):
    """
    Page Model 
    """
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True,\
            help_text=_('please input a-z or 0-9'))
    parent = TreeForeignKey('self', null=True, blank=True,\
            related_name='children', db_index=True, verbose_name=_('parent'))
    content = RichTextUploadingField(_('content'), null=True, blank=True)
    link = models.URLField(_('link'), blank=True, null=True)
    template = models.CharField(_('template'), max_length=200,\
            default='default')
    is_show = models.BooleanField(_('is show'), default=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    def __str__(self):
        return self.title

    def get_description(self, count=200):
        """Get description, default 200 words"""
        #return strip_tags(self.content)[0:200]
        return bleach.clean(strip_tags(self.content), strip=True)[0:count]

    def get_cover(self):
        """Get page's cover, use the first image of content"""
        tree = BeautifulSoup(self.content, "html5lib")
        cover = tree.find('img')
        if cover:
            return cover['src']
        else:
            return ''

    def get_link(self):
        """Get page' link"""
        if self.link:
            return self.link
        else:
            return 'http://%s/%s' % (settings.ALLOWED_HOSTS[0], self.slug)


    class Meta(object):
        verbose_name = _('page')
        verbose_name_plural = _('page')

    class MPTTMeta:
        order_insertion_by = ['title']
