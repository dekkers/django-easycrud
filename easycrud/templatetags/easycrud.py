from django import template
from django.conf import settings
from ..utils import get_model_by_name

register = template.Library()


@register.inclusion_tag("easycrud/object_heading.html", takes_context=True)
def easy_object_heading(context, obj):
    if not obj:
        obj = context['object']
    return {'object': obj, 'model_title': obj._meta.verbose_name.capitalize()}


@register.simple_tag
def easy_heading(model):
    if isinstance(model, basestring):
        model = get_model_by_name(model)
    title = model._meta.verbose_name_plural.capitalize()
    if model.has_create:
        return '<h3>{0} <a href="{1.create_url}"><img src="{2}admin/img/icon_addlink.gif"></a></h3>'.format(title, model, settings.STATIC_URL)
    else:
        return '<h3>{0}</h3>'.format(title)


@register.inclusion_tag("easycrud/object_list.html", takes_context=True)
def easy_list(context, object_list=None):
    if not object_list:
        if 'object_list' in context:
            object_list = context['object_list']
        else:
            object_list = []
    return {'object_list': object_list}
