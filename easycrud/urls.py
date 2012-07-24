from django.conf.urls import patterns, url
from django.db.models.loading import get_models

from .models import EasyCrudModel
from .views import ListView, CreateView, DetailView, UpdateView, DeleteView


def easycrud_urlpatterns():
    model_list = [m for m in get_models() if issubclass(m, EasyCrudModel)]
    pattern_list = []

    for model in model_list:
        name = model.model_name.replace(' ', '')
        url_list = []

        url_list.append(url('^%s/$' % name, ListView.as_view(model=model), name='%s_list' % name))
        url_list.append(url('^%s/(?P<pk>\d+)/$' % name, DetailView.as_view(model=model), name='%s_detail' % name))
        if model.has_create:
            url_list.append(url('^%s/create/$' % name, CreateView.as_view(model=model), name='%s_create' % name))
        if model.has_update:
            url_list.append(url('^%s/(?P<pk>\d+)/update/$' % name, UpdateView.as_view(model=model), name='%s_update' % name))
        if model.has_delete:
            url_list.append(url('^%s/(?P<pk>\d+)/delete/$' % name, DeleteView.as_view(model=model), name='%s_delete' % name))

        pattern_list += patterns('', *url_list)

    return pattern_list