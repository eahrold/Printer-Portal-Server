'''Printer URLs'''
from django.conf.urls import patterns, url

from printers.views import ModelCreateView, \
    ModelUpdateView, \
    ManageView, \
    IndexView, \
    toggle_printerlist_public, \
    get_printer_list, \
    get_subscription_list

from printers.views import *

from sparkle import views as sviews

from printers.models import Printer, PrinterList, Option, SubscriptionPrinterList
from printers.forms import *

urlpatterns = patterns('',
                       url(r'^$', IndexView.as_view(), name='index_view'),
                       url(r'^manage/$', ManageView.as_view(), name='manage'),
                       url(r'^sparkle/$', sviews.index, name='su-index'),

                       # Add Actions
                       url(r'^printer/add/$', ModelCreateView.as_view(model=Printer), {}, name='printer_add'), \
                       url(r'^printerlist/add/$', ModelCreateView.as_view(model=PrinterList), {}, name='printerlist_add'), \
                       url(r'^subscription_list/add/$', ModelCreateView.as_view(model=SubscriptionPrinterList), {}, name='subscription_list_add'), \
                       url(r'^options/add/$', ModelCreateView.as_view(model=Option), {}, name='options_add'), \

                       # Edit Actions
                       url(r'^printer/edit/(?P<pk>[\w-]+)$', ModelUpdateView.as_view(model=Printer), {}, name='printer_edit'), \
                       url(r'^printerlist/edit/(?P<pk>[\w-]+)$', ModelUpdateView.as_view(model=PrinterList), name='printerlist_edit'), \
                       url(r'^subscription_list/edit/(?P<pk>[\w-]+)$', ModelUpdateView.as_view(model=SubscriptionPrinterList), name='subscription_list_edit'), \
                       url(r'^options/edit/(?P<pk>[\w-]+)$', ModelUpdateView.as_view(model=Option), {}, name='options_edit'), \

                       # Delete Actions
                       url(r'^printer/delete/(?P<id>\d+)/$', object_delete, {'model_class': Printer}, name='printer_delete'), \
                       url(r'^printerlist/delete/(?P<id>\d+)/$', object_delete, {'model_class': PrinterList}, name='printerlist_delete'), \
                       url(r'^subscription_list/delete/(?P<id>\d+)/$', object_delete, {'model_class': SubscriptionPrinterList}, name='subscription_list_delete'), \
                       url(r'^options/delete/(?P<id>\d+)/$', object_delete, {'model_class': Option}, name='options_delete'), \

                       # Details
                       url(r'^printer/details/(?P<id>\d+)/$', DetailView.as_view(model = Printer), name='printer_details'), \
                       url(r'^printerlist/details/(?P<id>\d+)/$', DetailView.as_view(model = PrinterList), name='printerlist_details'), \

                       # Other
                       url(r'^printerlist/public/(?P<id>\d+)/', toggle_printerlist_public, {}, name='printerlist_public'), \
                       url(r'^subscribe/$', get_subscription_list, name='get_subscription_list'), \
                       url(r'^(?P<name>[^/]+)/view', display_printer_list, name='get_list'), \
                       url(r'^(?P<name>[^/]+)/$', get_printer_list, name='get_list'), \
                       )
