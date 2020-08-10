from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms.widgets import Widget

from ..models.fits import Customer, Visit
from .base import BootstrapFormMixin, ModelList, ModelDetail, ModelEdit, ModelNew


class CustomerNew(ModelNew):
    model = Customer
    fields = [
        'firstName', 'lastName', 'address', 'email', 'phoneMain', 'phoneAlt', 'dateOfBirth', 'height', 'inseam'
    ]


class CustomerEdit(ModelEdit):
    model = Customer
    fields = [
        'firstName', 'lastName', 'address', 'email', 'phoneMain', 'phoneAlt', 'dateOfBirth', 'height', 'inseam'
    ]

    def get_form(self, form_class=None):
        form = super(CustomerEdit, self).get_form(form_class)
        w: Widget = form.fields["address"].widget
        w.attrs["rows"] = 3
        return form


class CustomerDelete(DeleteView):
    model = Customer
    success_url = reverse_lazy('customer-list')


class CustomerDetail(ModelDetail):
    model = Customer

    def get_tabs(self):
        return [
            {"tab_id": "profile", "tab_label": "Profile"},
            {"tab_id": "visits", "tab_label": "Visits"},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer: Customer = self.object
        customer.avatar = customer.asset_by_tag("_photo")
        context["avatar"] = {
            "fallback": "/static/image/person.png",
            "button_label": "Set Photo",
            "alt_text": f"{customer.firstName} {customer.lastName}",
            "tag": "_photo",
        }
        return context


class CustomerList(ModelList):
    model = Customer


class VisitEdit(UpdateView, BootstrapFormMixin):
    model = Visit
    fields = [
        'firstName', 'lastName', 'address', 'email', 'phoneMain', 'phoneAlt', 'dateOfBirth', 'height', 'inseam'
    ]


class VisitDetail(ModelDetail):
    model = Visit

    def get_tabs(self):
        return [
            {"tab_id": "profile", "tab_label": "Details"},
            {"tab_id": "visits", "tab_label": "Fitsheets"},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visit: Visit = self.object
        visit.avatar = visit.customer.asset_by_tag("_photo")
        context["avatar"] = {
            "fallback": "/static/image/person.png",
            "button_label": "Set Photo",
            "alt_text": f"{visit.customer.firstName} {visit.customer.lastName}",
            "tag": "_photo",
        }
        return context


class VisitNew(CreateView, BootstrapFormMixin):
    model = Visit
    fields = [
        'firstName', 'lastName', 'address', 'email', 'phoneMain', 'phoneAlt', 'dateOfBirth', 'height', 'inseam'
    ]


