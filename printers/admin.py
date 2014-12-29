'''Admin module'''
from django.contrib import admin
from printers.models import Printer, PrinterList, Option

admin.site.register(Printer)
admin.site.register(PrinterList)
admin.site.register(Option)
