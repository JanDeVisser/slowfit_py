from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.forms.widgets import DateInput

from ..widgets.datetime import DatePickerInput


class BootstrapFormMixin(FormMixin):
    def get_form(self, form_class=None):
        form = super(BootstrapFormMixin, self).get_form(form_class)
        for bound_field in form:
            if isinstance(bound_field.field.widget, DateInput):
                bound_field.field.widget = DatePickerInput()
            bound_field.field.widget.attrs["class"] = "form-control"
        return form


class ModelDetail(DetailView):
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model.__name__.lower()
        context.update({
            "mode": "detail",
            "user": self.request.user,
            "model": model_name,
            "editurl": f"{model_name}-edit"
        })
        if hasattr(self, "get_tabs") and callable(self.get_tabs):
            tabs = self.get_tabs()
            for tab in tabs:
                if "html" not in tab:
                    tab["html"] = f"slowfit/{model_name}_detail_{tab['tab_id']}.html"
            context["tabs"] = tabs
        return context


class ModelEditMixin(BootstrapFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model.__name__.lower()
        context.update({
            "mode": "edit",
            "user": self.request.user,
            "model": model_name,
            "cancelurl": f"{model_name}-list"
        })
        return context


class ModelEdit(UpdateView, ModelEditMixin):
    template_name_suffix = "_edit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model.__name__.lower()
        context["cancelurl"] = f"{model_name}-view"
        return context


class ModelNew(CreateView, ModelEditMixin):
    template_name_suffix = "_new"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model.__name__.lower()
        context["cancelurl"] = f"{model_name}-list"
        return context


class ModelList(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "mode": "list",
            "user": self.request.user,
            "model": self.model.__name__.lower()
        })
        return context
