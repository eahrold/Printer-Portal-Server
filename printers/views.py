'''Views'''
import datetime
from plistlib import writePlistToString

from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.core.urlresolvers import reverse

from sparkle.models import Version

from printer_portal.utils import get_client_ip, \
                                 site_info

from printers.models import Printer, \
                            PrinterList, \
                            Option, \
                            SubscriptionPrinterList, \
                            PPClientGitHubRelease

from printers.forms import PrinterForm, \
                           PrinterListForm, \
                           OptionForm, \
                           SubscriptionPrinterListForm

from printers.utils import generate_printer_dict_from_list, \
                           auto_process_form, \
                           github_latest_release


class ProtectedView(TemplateView):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedView, self).dispatch(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ProtectedView, self).__init__(*args, **kwargs)



class IndexView(TemplateView):
    '''Index page view'''
    template_name = 'printers/index.html'
    request = None

    def __init__(self, *args, **kwargs):
        super(IndexView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(IndexView, self).get_context_data(**kwargs)

        # add the static items to the context
        context['organization'] = settings.ORGANIZATION_NAME

        # Add in the querysets to
        context['printerlists'] = PrinterList.objects.filter(public=True)

        # Create a BOOL indicating whether there are any subscription lists
        context['subscriptions'] = SubscriptionPrinterList.objects.all().count() > 0

        # create the context for the verson_url
        version_url = None
        if settings.HOST_SPARKLE_UPDATES:
            version = Version.objects.filter(
                application__name=settings.APP_NAME,
                active=True).order_by('-published')
            if version:
                version_url = version[0].update.url

        # If we're not hosting updates, or it has yet to be configured
        # with any releases, use the client's GitHub release page.
        if not version_url:
            # We only need one object, so get it or create it
            version = PPClientGitHubRelease.objects.first()

            if not version:
                print 'Creating new PPClientGitHubRelease'
                version = PPClientGitHubRelease()

            # Only check-in with GitHub once a day for new releases
            # use the locally stored value every other time
            today = datetime.date.today()
            last_checked = version.last_checked
            version_url = version.url

            print "%s vs %s" % (today, last_checked)
            if not last_checked or last_checked < today:
                print "Getting latest GitHub release...."
                # version_url = github_latest_release(settings.GITHUB_LATEST_RELEASE)
                if version_url:
                    version.url = version_url

                version.last_checked = today
                print "NEW %s vs %s" % (version.last_checked, today)

                version.save()

        if version_url:
            context['version'] = version_url

        #Construct the site url used with the template tags
        #to generate the printer_portal(s) registered uri and
        #xml url for the printerlists
        context['site_info'] = site_info(self.request)

        return context


class ManageView(ProtectedView):
    template_name = 'printers/manage.html'
    request = None

    def get(self, request, **kwargs):
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
    template_name = 'printers/forms/base_form.html'
    model = None
    form_class = None
    object = None

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
def object_delete(request, pk, **kwargs):
    model_class = kwargs.get('model_class')
    if model_class:
        instance = get_object_or_404(model_class, pk=pk)
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
        super(DetailView, self).__init__()
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
## The following views have no tempate associated with them and generate    #
## xml data used in the client app, or displayed in a browser.              #
#############################################################################
def handle_printer_list_request(request, name, \
                                content_type='application/x-plist'):

    printer_list_object = get_object_or_404(PrinterList, name=name)

    plist = None
    if printer_list_object:
        p_dict = generate_printer_dict_from_list(request, printer_list_object)
        plist = writePlistToString(p_dict)

    return HttpResponse(plist, content_type)


def display_printer_list(request, name):
    '''Display xml data for the in a browser.'''
    return handle_printer_list_request(
        request, name, content_type='application/xml')


def get_printer_list(request, name):
    '''Get xml data for the client app.'''
    return handle_printer_list_request(request, name)


def show_printer_list(request, name):
    '''Display the xml plist for the client.'''
    printer_list_object = get_object_or_404(PrinterList, name=name)

    plist = None
    if printer_list_object:
        p_dict = generate_printer_dict_from_list(request, printer_list_object)
        plist = writePlistToString(p_dict)

    return HttpResponse(plist, content_type='application/x-plist')


def get_subscription_list(request):
    '''Get the printers for a given subnet.'''
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
