from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from ..utils import get_model_by_name

register = template.Library()


@register.simple_tag
def easy_object_show(obj):
    html = mark_safe("<table>")
    for field in obj._meta.fields:
        if field == obj._meta.auto_field or field.name in obj._easycrud_meta.exclude:
            continue
        if (hasattr(obj, '_easycrud_meta') and
            field.name == obj._easycrud_meta.owner_ref):
            continue
        html += format_html("<tr><th>{0}:</th><td>{1}</td></tr>", field.name, getattr(obj, field.name))
    html += mark_safe("</table>")
    return html


@register.inclusion_tag("easycrud/object_heading.html", takes_context=True)
def easy_object_heading(context, obj):
    if not obj:
        obj = context['object']
    return {'object': obj, 'model_title': obj._meta.verbose_name.capitalize()}


@register.simple_tag
def easy_heading(model):
    if isinstance(model, str):
        model = get_model_by_name(model)
    title = model._meta.verbose_name_plural.capitalize()
    if model.has_create:
        return format_html('<h3>{0} <a href="{1}"><img src="{2}admin/img/icon-addlink.svg"></a></h3>',
                           title, model.create_url, settings.STATIC_URL)
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
