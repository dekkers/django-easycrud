from django.views.generic import (ListView as DjangoListView, DetailView as DjangoDetailView,
                                  UpdateView as DjangoUpdateView, CreateView as DjangoCreateView,
                                  DeleteView as DjangoDeleteView)

from django.contrib.auth.decorators import login_required
from django.forms import ModelChoiceField

from .models import EasyCrudModel


class EasyCrudMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.owner_ref = self.model._easycrud_meta.owner_ref
        if self.owner_ref:
            # This is a hack to be able to conditionally use the login_required
            # decorator.
            ret = login_required(lambda request: False)(request)
            if ret:
                return ret
            profile = request.user.get_profile()
            self.owner_ref_obj = getattr(profile, self.owner_ref)
        return super(EasyCrudMixin, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(EasyCrudMixin, self).get_queryset()
        if self.owner_ref:
            kwargs = {self.owner_ref: self.owner_ref_obj}
            queryset = queryset.filter(**kwargs)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(EasyCrudMixin, self).get_context_data(**kwargs)
        context['model_name'] = self.model.model_name
        # Implement https://code.djangoproject.com/ticket/16744 here
        if 'view' not in context:
            context['view'] = self
        return context

    def get_form_class(self):
        form_class = super(EasyCrudMixin, self).get_form_class()
        if self.owner_ref:
            # Never display the owner field, as we always set it on the object
            # in get_form() below
            if self.owner_ref in form_class.base_fields:
                del form_class.base_fields[self.owner_ref]

            # Changing all ModelChoiceFields so the queryset only contains
            # objects owned by the current user. This will only list those items
            # on the form and also accept only those values during validation.
            for field in form_class.base_fields.values():
                if (isinstance(field, ModelChoiceField) and
                    issubclass(field.queryset.model, EasyCrudModel) and
                    field.queryset.model._easycrud_meta.owner_ref == self.owner_ref):
                    kwargs = {self.owner_ref: self.owner_ref_obj}
                    field.queryset = field.queryset.filter(**kwargs)
        return form_class

    def get_form(self, form_class):
        form = super(EasyCrudMixin, self).get_form(form_class)
        if self.owner_ref:
            setattr(form.instance, self.owner_ref, self.owner_ref_obj)
        return form


class ListView(EasyCrudMixin, DjangoListView):
    def get_template_names(self):
        names = super(ListView, self).get_template_names()
        names.append("easycrud/list.html")
        return names


class CreateView(EasyCrudMixin, DjangoCreateView):
    def get_template_names(self):
        names = super(CreateView, self).get_template_names()
        names.append("easycrud/createupdate.html")
        return names


class DetailView(EasyCrudMixin, DjangoDetailView):
    def get_template_names(self):
        names = super(DetailView, self).get_template_names()
        names.append("easycrud/detail.html")
        return names


class UpdateView(EasyCrudMixin, DjangoUpdateView):
    def get_template_names(self):
        names = super(UpdateView, self).get_template_names()
        names.append("easycrud/createupdate.html")
        return names


class DeleteView(EasyCrudMixin, DjangoDeleteView):
    def get_template_names(self):
        names = super(DeleteView, self).get_template_names()
        names.append("easycrud/delete.html")
        return names