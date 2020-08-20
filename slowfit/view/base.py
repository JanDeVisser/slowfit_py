from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormMixin
from django.forms.widgets import DateInput, DateTimeInput

from ..widgets.datetime import DatePickerInput, DateTimePickerInput


class BootstrapFormMixin(FormMixin):
    def get_form(self, form_class=None):
        form = super(BootstrapFormMixin, self).get_form(form_class)
        for bound_field in form:
            if isinstance(bound_field.field.widget, DateInput):
                bound_field.field.widget = DatePickerInput()
            elif isinstance(bound_field.field.widget, DateTimeInput):
                bound_field.field.widget = DateTimePickerInput()
            bound_field.field.widget.attrs["class"] = "form-control"
        return form


class ModelDetail(DetailView):
    context_object_name = 'object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.get_model().__name__.lower()
        context.update({
            "mode": "detail",
            "user": self.request.user,
            "model": model_name,
            "editurl": f"{model_name}-edit"
        })
        if hasattr(self, "get_tabs") and callable(self.get_tabs):
            tabs = self.get_tabs()
            if "tab" in self.kwargs:
                context["active_tab"] = self.kwargs["tab"]
            active = None
            for tab in tabs:
                if "html" not in tab:
                    tab["html"] = f"slowfit/{model_name}_detail_{tab['tab_id']}.html"
                if "class" not in tab:
                    cls = ""
                    if tab['tab_id'] == self.kwargs.get("tab"):
                        active = tab
                        cls = "active"
                    tab["class"] = cls
                elif tab["class"] == "active":
                    active = tab
            if active is None and len(tabs) > 0:
                tabs[0]["class"] = "active"
            context["tabs"] = tabs
        return context

    def get_model(self):
        return self.model


class ModelEditMixin(BootstrapFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.get_model().__name__.lower()
        context.update({
            "mode": "edit",
            "user": self.request.user,
            "model": model_name,
            "cancelurl": f"{model_name}-list"
        })
        return context

    def get_model(self):
        return self.model


class ModelEdit(UpdateView, ModelEditMixin):
    template_name_suffix = "_edit"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = context["model"]
        context["cancelurl"] = f"{model_name}-view"
        return context


class ModelNew(CreateView, ModelEditMixin):
    template_name_suffix = "_new"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = context["model"]
        context["cancelurl"] = f"{model_name}-list"
        return context


class ModelList(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "mode": "list",
            "user": self.request.user,
            "model": self.get_model().__name__.lower()
        })
        return context

    def get_model(self):
        return self.model
