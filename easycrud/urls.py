from django.conf import settings
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.db.models.loading import get_models

extra_views_available = True

try:
    from extra_views import InlineFormSet
except ImportError:
    extra_views_available = False


from .forms import get_form_class
from .models import EasyCrudModel
from .views import ListView, CreateView, DetailView, UpdateView, DeleteView, EasyCrudFormsetMixin
if extra_views_available:
    from .views import CreateWithInlinesView, UpdateWithInlinesView
from .utils import get_model_by_name


def easycrud_urlpatterns():
    model_list = [m for m in get_models() if issubclass(m, EasyCrudModel)]
    pattern_list = []

    for model in model_list:
        name = model.model_name.replace(' ', '')
        url_list = []

        url_list.append(url('^%s/$' % name, ListView.as_view(model=model), name='%s_list' % name))
        url_list.append(url('^%s/(?P<pk>\d+)/$' % name, DetailView.as_view(model=model), name='%s_detail' % name))
        if model._easycrud_meta.inline_models:
            if 'dynamic_formset' not in settings.INSTALLED_APPS:
                raise ImproperlyConfigured('The dynamic-formset app needs to be installed to use inline models')
            if not extra_views_available:
                raise ImproperlyConfigured('The extra-views app needs to be available to use inline models')
            inlines = []
            for inline in model._easycrud_meta.inline_models:
                if isinstance(inline, dict):
                    model_name = inline['model']
                    attrs = inline.copy()
                    if 'form_class' in attrs and isinstance(attrs['form_class'], basestring):
                        attrs['form_class'] = get_form_class(attrs['form_class'])
                else:
                    model_name = inline
                    attrs = {}
                attrs['model'] = get_model_by_name(model_name)
                attrs['extra'] = 0
                inlines.append(type(model_name + 'Inline', (EasyCrudFormsetMixin, InlineFormSet), attrs))
            if model.has_create:
                url_list.append(url('^%s/create/$' % name, CreateWithInlinesView.as_view(model=model, inlines=inlines), name='%s_create' % name))
            if model.has_update:
                url_list.append(url('^%s/(?P<pk>\d+)/update/$' % name, UpdateWithInlinesView.as_view(model=model, inlines=inlines), name='%s_update' % name))
        else:
            if model.has_create:
                url_list.append(url('^%s/create/$' % name, CreateView.as_view(model=model), name='%s_create' % name))
            if model.has_update:
                url_list.append(url('^%s/(?P<pk>\d+)/update/$' % name, UpdateView.as_view(model=model), name='%s_update' % name))
        if model.has_delete:
            url_list.append(url('^%s/(?P<pk>\d+)/delete/$' % name, DeleteView.as_view(model=model), name='%s_delete' % name))

        pattern_list += patterns('', *url_list)

    return pattern_list
