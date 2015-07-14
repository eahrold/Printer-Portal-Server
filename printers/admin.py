'''Admin module'''
from django.contrib import admin
from printers.models import Printer, \
                            PrinterList, \
                            SubscriptionPrinterList, \
                            Option, \
                            PPClientGitHubRelease


registry = [ Printer, \
             PrinterList, \
             SubscriptionPrinterList, \
             Option, \
             PPClientGitHubRelease
            ]

for model_class in registry:
    admin.site.register(model_class)
