import django
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.forms.widgets import Widget
from django.shortcuts import get_object_or_404, redirect, render

from ..models.fits import Customer, Visit, FitSheet, RoadFitSheet, TTFitSheet, Trial
from .base import ModelList, ModelDetail, ModelEdit, ModelNew


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


class VisitEdit(ModelEdit):
    model = Visit
    fields = [
        'purpose', 'experience', 'goals', 'injuries', 'customerConcerns', 'fitterConcerns', 'pedalSystem',
        'hy', 'hx', 'sy', 'sx', 'crankLength', 'saddle', 'saddleHeight', 'saddleSetback', 'saddleBarDrop'
    ]


class VisitDetail(ModelDetail):
    model = Visit

    def get_tabs(self):
        return [
            {"tab_id": "details", "tab_label": "Details"},
            {"tab_id": "fits", "tab_label": "Fitsheets"},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        visit: Visit = self.object
        visit.avatar = visit.customer.asset_by_tag("_photo")
        context["avatar"] = {
            "fallback": "/static/image/person.png",
            "button_label": "Set Photo",
            "alt_text": f"{visit.customer}",
            "tag": "_photo",
        }
        return context


class VisitNew(ModelNew):
    model = Visit
    fields = [
        'date', 'purpose', 'experience', 'goals', 'injuries', 'customerConcerns', 'fitterConcerns', 'pedalSystem',
        'hy', 'hx', 'sy', 'sx', 'crankLength', 'saddle', 'saddleHeight', 'saddleSetback', 'saddleBarDrop'
    ]

    def get_context_data(self, **kwargs):
        context = super(VisitNew, self).get_context_data(**kwargs)
        context["customer"] = Customer.objects.filter(id=self.kwargs["customer_id"]).first()
        context["cancelurl"] = "customer-view"
        context["cancelurl_param"] = self.kwargs["customer_id"]
        return context

    def form_valid(self, form):
        form.instance.customer = Customer.objects.filter(id=self.kwargs["customer_id"]).first()
        return super(VisitNew, self).form_valid(form)


class FitSheetView:
    def get_queryset(self):
        return self.get_model().objects.all()

    def get_model(self):
        return TTFitSheet if self.kwargs["fit_type"] == "TT" else RoadFitSheet


# class FitSheetNew(ModelNew, FitSheetView):
class FitSheetNew(FitSheetView, ModelNew):
    fields = ['description']
    template_name = "slowfit/fitsheet_new.html"

    def get_context_data(self, **kwargs):
        context = super(FitSheetNew, self).get_context_data(**kwargs)
        context["visit"] = Visit.objects.get(pk=self.kwargs["visit_id"])
        context["cancelurl"] = "visit-view"
        context["cancelurl_param"] = self.kwargs["visit_id"]
        return context

    def form_valid(self, form):
        form.instance.visit = Visit.objects.get(pk=self.kwargs["visit_id"])
        return super(FitSheetNew, self).form_valid(form)


class FitSheetDetail(ModelDetail):
    template_name = "slowfit/fitsheet_detail.html"

    def get_tabs(self):
        return [
            {"tab_id": "details", "tab_label": "Details", "html": "slowfit/fitsheet_detail_details.html"},
            {"tab_id": "trials", "tab_label": "Trials", "html": "slowfit/fitsheet_detail_trials.html"},
        ]

    def get_context_data(self, **kwargs):
        context = super(FitSheetDetail, self).get_context_data(**kwargs)
        fit: FitSheet = self.object
        fit.avatar = fit.visit.customer.asset_by_tag("_photo")
        context["avatar"] = {
            "fallback": "/static/image/person.png",
            "button_label": "Set Photo",
            "alt_text": f"{fit.visit.customer}",
            "tag": "_photo",
        }
        context["editurl"] = "fitsheet-edit"
        context["active_tab"] = self.kwargs.get("tab")
        return context

    def get_queryset(self):
        fit_sheet: FitSheet = FitSheet.objects.get(pk=self.kwargs["pk"])
        if fit_sheet.roadfitsheet is not None:
            self.model = RoadFitSheet
            return RoadFitSheet.objects.all().filter(pk=self.kwargs["pk"])
        else:
            self.model = TTFitSheet
            return TTFitSheet.objects.all().filter(pk=self.kwargs["pk"])


class FitSheetEdit(ModelEdit, FitSheetView):
    model = RoadFitSheet
    fields = [
        'hy', 'hx', 'webY', 'webX', 'sy', 'sx', 'crankLength', 'saddle', 'saddleHeight', 'saddleSetback',
        'saddleBarDrop', 'barWidth', 'barDrop', 'barReach'
    ]


class TrialForm(django.forms.ModelForm):
    class Meta:
        model = Trial
        fields = ['hx', 'hy', 'sx', 'sy']

    hx = django.forms.IntegerField(min_value=200, max_value=700)
    hy = django.forms.IntegerField(min_value=400, max_value=900)
    sx = django.forms.IntegerField(min_value=-400, max_value=400)
    sy = django.forms.FloatField(min_value=400, max_value=900)


class NewTrialForm(TrialForm):
    class Meta:
        model = Trial
        fields = ['fitSheet', 'hx', 'hy', 'sx', 'sy']

    fitSheet = django.forms.ModelChoiceField(queryset=FitSheet.objects.all())


def trial_create(request, fitsheet_id):
    form = NewTrialForm(request.POST)
    if form.is_valid():
        trial: Trial = form.save()
        return HttpResponseRedirect(trial.get_absolute_url())
    else:
        return render(request, reverse('fitsheet-view-tab', kwargs={'pk': fitsheet_id, 'tab': 'trials'}),
                      {'form_new': form})


def trial_update(request, pk):
    trial = get_object_or_404(Trial, pk=pk)
    if request.method == "POST":
        form = TrialForm(request.POST, instance=trial)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(trial.get_absolute_url())
        else:
            return render(request, reverse('fitsheet-view-tab', kwargs={'pk': fitsheet_id, 'tab': 'trials'}), {'form_new': form})


def trial_delete(request, pk):
    trial = get_object_or_404(Trial, pk=pk)
    fitsheet = trial.fitSheet_id
    trial.delete()
    redirect('fitsheet-view-tab', fitsheet, 'trials')
