'''Views'''
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.conf import settings

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator

from django.template import RequestContext, Template
from django.template.loader import get_template

from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.core.urlresolvers import reverse

from urlparse import urlunparse
from plistlib import writePlistToString
import datetime

from sparkle.models import Version, GitHubVersion

from printer_portal.utils import get_client_ip, \
    site_info

from printers.models import Printer, PrinterList, Option, SubscriptionPrinterList
from printers.forms import PrinterForm, PrinterListForm, OptionForm, SubscriptionPrinterListForm
from printers.utils import generate_printer_dict_from_list, \
    auto_process_form, \
    github_latest_release


class ProtectedView(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)


class IndexView(TemplateView):

    '''Index page view'''
    template_name = 'printers/index.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)

        # add the static items to the context
        context['organization'] = settings.ORGANIZATION_NAME

        # Add in the querysets to
        context['printerlists'] = PrinterList.objects.filter(public=True)
        context[
            'subscriptions'] = SubscriptionPrinterList.objects.all().count() > 0

        # create the context for the verson_url
        version_url = None
        if settings.HOST_SPARKLE_UPDATES:
            version = Version.objects.filter(
                application__name=settings.APP_NAME,
                active=True).order_by('-published')
            if version:
                version_url = version[0].update.url

        # If we're not hosting updates, or it has yet to be configured
        # with any releases, use the GitHub project page's release.
        if not version_url:
            # We only need one object, so get it or create it
            try:
                version = GitHubVersion.objects.filter(pk=1)[0]
            except IndexError:
                version = GitHubVersion()

            # Only check-in with GitHub once a day for new releases
            # use the locally stored value every other time
            today = datetime.datetime.today
            last_checked = version.url
            version_url = version.url

            if not last_checked or not version_url or last_checked < today:
                version_url = github_latest_release(settings.GITHUB_LATEST_RELEASE)
                if version_url:
                    version.url = version_url
                    version.last_checked = today()
                    version.save()

        if version_url:
            context['version'] = version_url

        '''Construct the site url used with the template tags
        to generate the printer_portal(s) registered uri and
        xml url for the printerlists'''

        context['site_info'] = site_info(self.request)

        return context


class ManageView(ProtectedView):
    template_name = 'printers/manage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(ManageView, self).get_context_data(**kwargs)

        printerlists = PrinterList.objects.all()
        subscription_lists = SubscriptionPrinterList.objects.all()
        printers = Printer.objects.all()
        options = Option.objects.all()

        context['printerlists'] = printerlists
        context['subscription_lists'] = subscription_lists
        context['printers'] = printers
        context['options'] = options

        '''Construct the site url used with the template tags
        to generate the printerportal(s) registered uri and
        xml url for the printerlists'''

        context['site_info'] = site_info(self.request)

        return context


class BaseFormView(FormView):
    model = None
    template_name = 'printers/forms/base_form.html'
    form_class = None

    def form_valid(self, form):
        self.object = form.save(commit=True)

        # The printer model has an extra potential step of creating
        # a new option at the time of creating a new printer object
        if self.model == Printer:
            new_option = form.cleaned_data['new_option']
            if new_option:
                obj = Option.objects.get_or_create(option=new_option)
                self.object.options.add(obj[0].pk)
                self.object.save()

        return super(BaseFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('manage')

    def __init__(self, *args, **kwargs):
        model = kwargs.get('model')
        form_class = kwargs.get('form_class')
        # If a form_class is not provided at init
        # set it using the model key
        if model and not form_class:
            if model == Printer:
                self.form_class = PrinterForm
            if model == Option:
                self.form_class = OptionForm
            elif model == PrinterList:
                self.form_class = PrinterListForm
            elif model == SubscriptionPrinterList:
                self.form_class = SubscriptionPrinterListForm

        super(BaseFormView, self).__init__(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BaseFormView, self).dispatch(*args, **kwargs)


class ModelCreateView(BaseFormView, CreateView):

    '''Base Create View'''
    pass


class ModelUpdateView(BaseFormView, UpdateView):

    '''Base Update View'''
    pass


@login_required(redirect_field_name='')
def object_delete(request, id, **kwargs):
    model_class = kwargs.get('model_class')
    if model_class:
        instance = get_object_or_404(model_class, pk=id)
        instance.delete()
    return redirect('manage')


#########################################
#######  Details functions ##############
#########################################

class DetailView(ProtectedView):
    model = None
    template_name = None
    model_key = None

    def __init__(self, model):
        self.model = model
        if model == Printer:
            self.template_name = 'printers/printer_details.html'
        elif model == PrinterList:
            self.template_name = 'printers/printerlist_details.html'


    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        object = get_object_or_404(self.model, pk=kwargs.get('id'))
        if object:
            context['instance'] = object

        return context

@login_required(redirect_field_name='')
def toggle_printerlist_public(request, id):
    '''Toggle the printer list public/private'''
    instance = get_object_or_404(PrinterList, pk=id)
    instance.public = not instance.public
    instance.save()
    return redirect('manage')


#############################################################################
## This is the request that returns the plist for the Printer-Portal.app    #
##  it should  be the only area that requires no login                      #
#############################################################################
def handle_printer_list_request(
        request, name, content_type='application/x-plist'):
    printer_list_object = get_object_or_404(PrinterList, name=name)

    plist = None
    if printer_list_object:
        p_dict = generate_printer_dict_from_list(request, printer_list_object)
        plist = writePlistToString(p_dict)

    return HttpResponse(plist, content_type)


def display_printer_list(request, name):
    '''display xml data for the in a browser'''
    return handle_printer_list_request(
        request, name, content_type='application/xml')


def get_printer_list(request, name):
    '''get xml data for the client app'''
    return handle_printer_list_request(request, name)


def show_printer_list(request, name):
    '''display the xml plist for the client'''
    printer_list_object = get_object_or_404(PrinterList, name=name)

    plist = None
    if printer_list_object:
        p_dict = generate_printer_dict_from_list(request, printer_list_object)
        plist = writePlistToString(p_dict)

    return HttpResponse(plist, content_type='application/x-plist')


def get_subscription_list(request):
    '''get the printers avaliable for a given subnet'''
    response = None

    client_ip = get_client_ip(request)
    printer_list_object = SubscriptionPrinterList.instance_for_ip(client_ip)

    plist = None
    if printer_list_object:
        p_dict = generate_printer_dict_from_list(request, printer_list_object)
        p_dict['subnet'] = printer_list_object.subnet

        plist = writePlistToString(p_dict)
        response = HttpResponse(plist, content_type='application/x-plist')
    else:
        response = HttpResponseNotFound()

    return response
