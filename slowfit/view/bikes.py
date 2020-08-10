from django.forms import inlineformset_factory
import django.forms
from django.http import HttpRequest, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import get_object_or_404

from ..models.bikes import Brand, Frame, FrameSize
from .base import ModelList, ModelDetail


class BrandDetail(ModelDetail):
    model = Brand

    def get_tabs(self):
        return [
            {"tab_id": "general", "tab_label": "General"},
            {"tab_id": "frames", "tab_label": "Frames"},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand: Brand = self.object
        brand.avatar = brand.asset_by_tag("_logo")
        context["avatar"] = {
            "fallback": "/static/image/bicycle.png",
            "button_label": "Set logo",
            "alt_text": f"{brand.name} logo",
            "tag": "_logo",
        }
        return context


class BrandList(ModelList):
    model = Brand


class FrameSizeForm(django.forms.ModelForm):
    class Meta:
        model = FrameSize
        fields = ['name', 'stack', 'reach', 'headTubeAngle']

    name = django.forms.CharField(max_length=10)
    stack = django.forms.IntegerField(min_value=400, max_value=900)
    reach = django.forms.IntegerField(min_value=200, max_value=700)
    headTubeAngle = django.forms.FloatField(min_value=65.0, max_value=90.0)


class FrameDetail(ModelDetail):
    model = Frame
    FrameSizeFormSet = inlineformset_factory(Frame, FrameSize, form=FrameSizeForm,
                                             extra=1, fk_name="frame", can_delete=True)

    def get_tabs(self):
        return [
            {"tab_id": "general", "tab_label": "General"},
            {"tab_id": "sizes", "tab_label": "Size Run"},
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        frame: Frame = self.object
        frame.avatar = frame.asset_by_tag("_avatar")
        context["avatar"] = {
            "fallback": "/static/image/bicycle.png",
            "button_label": "Set Image",
            "alt_text": str(frame),
            "tag": "_avatar",
        }
        context["framesize_form"] = self.FrameSizeFormSet(instance=self.object)
        return context

    def post(self, request: HttpRequest, pk):
        frame = get_object_or_404(Frame, pk=pk)
        formset = self.FrameSizeFormSet(request.POST, instance=frame)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(request.get_full_path())
        else:
            for e in formset.errors:
                print(e)
            return HttpResponseServerError("Errors!")


class FrameList(ModelList):
    model = Frame


