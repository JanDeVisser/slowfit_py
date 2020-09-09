import logging
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View

import google_auth_oauthlib.flow
import google.oauth2.credentials

from django.shortcuts import render, get_object_or_404

from slowfit.models.base import RegisteredClasses, Asset

from .imports.gimport import SCOPES, GImportSession, ImportLog, Credentials
from .imports.jsonimport import JSONImportSession
from slowfit_py.settings import DEBUG

from .view.base import ModelDetail, ModelList

# See here for docs on google apps auth:
#    https://developers.google.com/identity/protocols/oauth2/web-server#python


@login_required
def clear_google_auth(request):
    if "credentials" in request.session:
        del request.session["credentials"]
    return HttpResponseRedirect("/imports")


@login_required
def import_google_sheet(request):
    context = {"initiated": False}
    if "sheetid" in request.POST:
        if "credentials" not in request.session or "refresh" in request.POST:
            return google_authorize(request)
        credentials = google.oauth2.credentials.Credentials(**request.session['credentials'])
        session = GImportSession(credentials, request.user)
        session.import_sheet(request.POST["sheetid"])
        request.session['credentials'] = Credentials(request.session['credentials'], credentials)
        context["initiated"] = True
    context["imports"] = ImportLog.objects.filter()
    context["user"] = request.user
    return render(request, "slowfit/import.html", context=context)


@login_required
def import_json_data(request):
    context = {"initiated": False}
    if "folder" in request.POST:
        session = JSONImportSession(request.user)
        session.import_data(request.POST["folder"], request.POST.get("brand"))
        context["initiated"] = True
    context["imports"] = ImportLog.objects.filter()
    context["user"] = request.user
    return render(request, "slowfit/import.html", context=context)


@login_required
def google_authorize(request):
    request.session["request_uri"] = request.build_absolute_uri()
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials.json', SCOPES)
    flow.redirect_uri = "http://localhost:8000/api/oauth2"
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session["oauth2_state"] = state
    return HttpResponseRedirect(authorization_url)


def oauth2(request):
    state = request.session.get('oauth2_state', None)
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials.json', scopes=SCOPES, state=state)
    flow.redirect_uri = "http://localhost:8000/api/oauth2"
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    request.session['credentials'] = Credentials(request.session.get('credentials'), flow.credentials)
    return HttpResponseRedirect(request.session["request_uri"])


def index(request):
    context = {}
    if hasattr(request, "user"):
        context["user"] = request.user
    return render(request, "slowfit/index.html", context=context)


def utils(request):
    context = {}
    if hasattr(request, "user"):
        context["user"] = request.user
    return render(request, "slowfit/utils.html", context=context)


def model_view(request, model, id):
    cls = RegisteredClasses.get_class(model)
    obj = cls.objects.get(pk=id)
    context = {
        "object": obj,
        "mode": "view",
        "user": request.user
    }
    context = obj.get_context(context) if hasattr(obj, "get_context") and callable(obj.get_context) else context
    return render(request, context.get("template", f"slowfit/{model}/view.html"), context=context)


def model_edit(request, model, id):
    cls = RegisteredClasses.get_class(model)
    obj = cls.objects.get(pk=id)
    context = {
        "object": obj,
        "mode": "edit",
        "user": request.user
    }
    context = obj.get_context(context) if hasattr(obj, "get_context") and callable(obj.get_context) else context
    return render(request, context.get("template", f"slowfit/{model}/edit.html"), context=context)


def model_new(request, model):
    cls = RegisteredClasses.get_class(model)
    context = {
        "class": cls,
        "mode": "new",
        "user": request.user
    }
    context = cls.get_class_context(context) \
        if hasattr(cls, "get_class_context") and callable(cls.get_class_context) \
        else context
    return render(request, context.get("template", f"slowfit/{model}/new.html"), context=context)


class AssetView(View):
    def get(self, request, id):
        asset = get_object_or_404(Asset, pk=id)
        with asset.asset.open() as f:
            data = f.read()
        response = HttpResponse(data, content_type=asset.mimeType)
        return response

    def delete(self, request):
        pass

    def post(self, request):
        pass


if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
