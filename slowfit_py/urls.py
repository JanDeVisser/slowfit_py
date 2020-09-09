"""slowfit_py URL Configuration

The `urlpatterns` list routes URLs to view. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function view
    1. Add an imports:  from my_app imports view
    2. Add a URL to urlpatterns:  path('', view.home, name='home')
Class-based view
    1. Add an imports:  from other_app.view imports Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls imports include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import slowfit.calculate
import slowfit.views
import slowfit.view.bikes
import slowfit.view.customer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', slowfit.views.index),
    path('api/oauth2/', slowfit.views.oauth2),
    path('gauthorize/', slowfit.views.google_authorize),
    path('clearauth/', slowfit.views.clear_google_auth),
    path('import/', slowfit.views.import_json_data, name='import'),
    path('googleimport/', slowfit.views.import_google_sheet, name='google-import'),
    path('calculate/', slowfit.calculate.calculate, name='calculate'),
    path('utils/', slowfit.views.utils, name='utils'),
    path('stackreach/', slowfit.calculate.calculate_stack_reach, name='stackreach'),
    path('asset/<int:id>', slowfit.views.AssetView.as_view(), name='asset'),
    path('asset/', slowfit.views.AssetView.as_view(), name='asset'),
    # path('<str:model>/<int:id>/', slowfit.view.model_view, name='model-view'),
    # path('<str:model>/<int:id>/edit', slowfit.view.model_edit, name='model-edit'),
    # path('<str:model>/new/', slowfit.view.model_new, name='model-new'),
    path('brand/', slowfit.view.bikes.BrandList.as_view(), name='brand-list'),
    path('brand/<int:pk>/', slowfit.view.bikes.BrandDetail.as_view(), name='brand-view'),
    path('frame/', slowfit.view.bikes.FrameList.as_view(), name='frame-list'),
    path('frame/<int:pk>/', slowfit.view.bikes.FrameDetail.as_view(), name='frame-view'),
    path('material/', slowfit.view.bikes.FrameList.as_view(), name='material-list'),
    path('material/<int:pk>/', slowfit.view.bikes.FrameDetail.as_view(), name='material-view'),
    path('biketype/', slowfit.view.bikes.FrameList.as_view(), name='biketype-list'),
    path('biketype/<int:pk>/', slowfit.view.bikes.FrameDetail.as_view(), name='biketype-view'),
    path('year/<int:year>/', slowfit.view.bikes.FrameDetail.as_view(), name='year-view'),
    path('customer/', slowfit.view.customer.CustomerList.as_view(), name='customer-list'),
    path('customer/<int:pk>/', slowfit.view.customer.CustomerDetail.as_view(), name='customer-view'),
    path('customer/new/', slowfit.view.customer.CustomerNew.as_view(), name='customer-new'),
    path('customer/<int:pk>/edit/', slowfit.view.customer.CustomerEdit.as_view(), name='customer-edit'),
    path('customer/<int:pk>/delete/', slowfit.view.customer.CustomerDetail.as_view(), name='customer-delete'),
    path('visit/<int:pk>/', slowfit.view.customer.VisitDetail.as_view(), name='visit-view'),
    path('visit/<int:pk>/edit', slowfit.view.customer.VisitEdit.as_view(), name='visit-edit'),
    path('visit/new/<int:customer_id>/', slowfit.view.customer.VisitNew.as_view(), name='visit-new'),
    path('fitsheet/<int:pk>/', slowfit.view.customer.FitSheetDetail.as_view(), name='fitsheet-view'),
    path('fitsheet/<int:pk>/<str:tab>/', slowfit.view.customer.FitSheetDetail.as_view(), name='fitsheet-view-tab'),
    path('fitsheet/<int:pk>/edit/', slowfit.view.customer.FitSheetEdit.as_view(), name='fitsheet-edit'),
    path('fitsheet/new/<int:visit_id>/<str:fit_type>/', slowfit.view.customer.FitSheetNew.as_view(), name='fitsheet-new'),
    path('trial/new/', slowfit.view.customer.trial_create, name='trial-new'),
    path('trial/<int:pk>/', slowfit.view.customer.trial_update, name='trial-edit'),
    path('trial/<int:pk>/delete/', slowfit.view.customer.trial_delete, name='trial-delete'),
]