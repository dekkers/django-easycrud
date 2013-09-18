from django.views.generic import (ListView as DjangoListView, DetailView as DjangoDetailView,
                                  UpdateView as DjangoUpdateView, CreateView as DjangoCreateView,
                                  DeleteView as DjangoDeleteView)
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms import ModelChoiceField

extra_views_available = True
try:
    from extra_views import UpdateWithInlinesView as StandardUpdateWithInlinesView, CreateWithInlinesView as StandardCreateWithInlinesView
except ImportError:
    extra_views_available = False

from .forms import get_form_class
from .models import EasyCrudModel
from .utils import get_model_by_name
from .widgets import EasyCrudSelect


def update_form_field(field, owner_ref, owner_ref_obj, update_widget=False):
    if (isinstance(field, ModelChoiceField) and
        issubclass(field.queryset.model, EasyCrudModel) and
        field.queryset.model._easycrud_meta.owner_ref == owner_ref):
        kwargs = {owner_ref: owner_ref_obj}
        field.queryset = field.queryset.filter(**kwargs)
        if update_widget:
            field.widget = EasyCrudSelect(model=field.queryset.model)


class EasyCrudMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.owner_ref = self.model._easycrud_meta.owner_ref
        if self.owner_ref:
            # This is a hack to be able to conditionally use the login_required
            # decorator.
            ret = login_required(lambda request: False)(request)
            if ret:
                return ret
            if request.user.is_staff:
                if self.owner_ref in request.GET:
                    model = get_model_by_name(self.owner_ref)
                    pk = request.GET[self.owner_ref]
                    self.owner_ref_obj = model.objects.get(pk=pk)
                else:
                    self.owner_ref_obj = getattr(request.user, self.owner_ref)
            else:
                self.owner_ref_obj = getattr(request.user, self.owner_ref)
            setattr(self, self.owner_ref, self.owner_ref_obj)
        if self.model._easycrud_meta.form_class:
            self.form_class = get_form_class(self.model._easycrud_meta.form_class)
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
        if self.model._easycrud_meta.exclude:
            for field_name in self.model._easycrud_meta.exclude:
                del form_class.base_fields[field_name]

        if self.owner_ref:
            # Never display the owner field, as we always set it on the object
            # in get_form() below
            if self.owner_ref in form_class.base_fields:
                del form_class.base_fields[self.owner_ref]

            # Changing all ModelChoiceFields so the queryset only contains
            # objects owned by the current user. This will only list those items
            # on the form and also accept only those values during validation.
            for field in form_class.base_fields.values():
                update_form_field(field, self.owner_ref, self.owner_ref_obj, update_widget=True)

        return form_class

    def get_form(self, form_class):
        form = super(EasyCrudMixin, self).get_form(form_class)
        if self.owner_ref:
            setattr(form.instance, self.owner_ref, self.owner_ref_obj)
        return form

    def get_success_url(self):
        if self.request.POST['success_url']:
            return self.request.POST['success_url']
        elif self.success_url:
            return self.success_url
        else:
            name = self.model.model_name.replace(' ', '')
            return reverse('%s_list' % name)


class EasyCrudFormsetMixin(object):
    def construct_formset(self):
        formset = super(EasyCrudFormsetMixin, self).construct_formset()
        self.owner_ref = self.model._easycrud_meta.owner_ref

        if self.owner_ref:
            self.owner_ref_obj = getattr(self.request.user, self.owner_ref)

            # Update the form fields in every form currently in the formset.
            for form in formset:
                for field in form.fields.values():
                    update_form_field(field, self.owner_ref, self.owner_ref_obj)

            # The formset's empty_form is created using the class stored in
            # formset.form, so we update that one too.
            for field in formset.form.base_fields.values():
                update_form_field(field, self.owner_ref, self.owner_ref_obj)

        return formset


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


if extra_views_available:
    class CreateWithInlinesView(EasyCrudMixin, StandardCreateWithInlinesView):
        def get_template_names(self):
            names = super(CreateWithInlinesView, self).get_template_names()
            names.append("easycrud/createupdatewithinlines.html")
            return names

    class UpdateWithInlinesView(EasyCrudMixin, StandardUpdateWithInlinesView):
        def get_template_names(self):
            names = super(UpdateWithInlinesView, self).get_template_names()
            names.append("easycrud/createupdatewithinlines.html")
            return names
