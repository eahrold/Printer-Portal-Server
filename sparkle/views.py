from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.sites.models import Site
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required

from forms import AppcastForm, PrivateKeyForm
from sparkle.models import Application,\
                           PrivateKey,\
                           Version,\
                           SystemProfileReport,\
                           SystemProfileReportRecord

from printer_portal.utils import site_info

@login_required(redirect_field_name='')
def index(request):
    versions = Version.objects.all()
    privateKey = PrivateKey.objects.all()

    site = Site.objects.get_current()
    context = {'versions': versions, 'site': site, 'privateKey': privateKey}

    return render_to_response(
        'sparkle/index.html', context, context_instance=RequestContext(request))


@login_required(redirect_field_name='')
def private_key_add(request):
    error = False
    if request.POST:
        if "cancel" in request.POST:
            return redirect('sparkle.views.index')

        form = PrivateKeyForm(request.POST, request.FILES)
        if form.is_valid():
            privateKey = form.save(commit=True)
            privateKey.save()
            return redirect('sparkle.views.index')
        else:
            error = True
    else:
        form = PrivateKeyForm()
    context = {'form': form, 'error': error}
    return render_to_response(
        'sparkle/forms/private_key.html', context, context_instance=RequestContext(request))


@login_required(redirect_field_name='')
def private_key_edit(request, pk):
    error = False
    privateKey = get_object_or_404(PrivateKey, pk=pk)
    if request.POST:
        if "cancel" in request.POST:
            return redirect('sparkle.views.index')

        form = PrivateKeyForm(request.POST, request.FILES, instance=privateKey)
        if form.is_valid():
            form.save()
            return redirect('sparkle.views.index')
    else:
        form = PrivateKeyForm(instance=privateKey)

    context = {'form': form, 'privateKey': privateKey, 'error': error}
    return render_to_response(
        'sparkle/forms/private_key.html', context, context_instance=RequestContext(request))


@login_required(redirect_field_name='')
def version_edit(request, pk):
    version = get_object_or_404(Version, pk=pk)
    if request.POST:
        form = AppcastForm(request.POST, request.FILES, instance=version)
        if form.is_valid():
            form.save()
        return redirect('sparkle.views.index')
    else:
        form = AppcastForm(instance=version)
    return render_to_response('sparkle/forms/version.html', {
                              'form': form, 'version': version}, context_instance=RequestContext(request))


@login_required(redirect_field_name='')
def version_add(request):
    if request.POST:
        form = AppcastForm(request.POST, request.FILES)
        if form.is_valid():
            version = form.save(commit=True)
            version.save()
        return redirect('sparkle.views.index')
    else:
        form = AppcastForm(
            initial={
                'application': Application.objects.get(
                    id=1)})
    return render_to_response(
        'sparkle/forms/version.html', {'form': form, }, context_instance=RequestContext(request))


@login_required(redirect_field_name='')
def version_delete(request, pk):
    version = get_object_or_404(Version, pk=pk)
    if version:
        version.delete()
    return redirect('sparkle.views.index')


@login_required(redirect_field_name='')
def version_activate(request, pk):
    version = get_object_or_404(Version, pk=pk)
    if version.active:
        version.active = False
    else:
        version.active = True
    version.save()
    return redirect('sparkle.views.index')

##########################################################################
### No Login Requierd Below This Point ###################################
##########################################################################

def appcast(request, name, testing=False):
    """Generate the appcast for the given application while recording any system profile reports"""
    application = None
    context = {}
    parameters = dict(request.GET)
    content_type = 'application/rss+xml'
    site = site_info(request)

    # Check if a parameter for testing was set (how the template specifies it)
    # the requst, or accessing the 'testing url' (how the test client would
    # specify)
    active = not parameters.get('testing', testing)
    # __default is defined in sparkle.urls context when someone access
    # the appcast by simply using "client" as the application specifier
    # e.g `http://server.com/sparkle/client/appcast.xml`
    # This is usefull when the site is only hosting a single application.
    if name == '__default':
        application = get_object_or_404(Application, pk=1)
    else:
        application = get_object_or_404(Application, name=name)

    # The template passes in the parameter "display=true" to indicate
    # the appcast should simply be displayed in the browser
    if parameters.get('display', False):
        content_type = 'application/xhtml+xml'

    # clean up the viewability parameters so we can
    # accurately determine if a report was submitted
    parameters.pop('testing', None)
    parameters.pop('display', None)

    if len(parameters):
        # create a report and records of the keys/values
        report = SystemProfileReport.objects.create(
            ip_address=request.META.get('REMOTE_ADDR'))

        for key, value in parameters.iteritems():
            record = SystemProfileReportRecord.objects.create(
                report=report,
                key=key,
                value=value)
            record.save()

    # get the latest versions
    versions = Version.objects.filter(
        application__name=application.name,
        active=active).order_by('-published')

    context = {'application': application, 'versions': versions, 'site': site}
    return render_to_response(
        'sparkle/appcast.xml', context, content_type=content_type)
