import os

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from printers.api_views import OptionViewSet, PrinterViewSet, PrinterListViewSet

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^changepassword/$', 'django.contrib.auth.views.password_change', name='change_password'),
    url(r'^changepassword/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    )

if settings.INCLUDE_REST_API:
    ROUTER = DefaultRouter()
    ROUTER.register(r'options', OptionViewSet)
    ROUTER.register(r'printers', PrinterViewSet)
    ROUTER.register(r'printerlists', PrinterListViewSet)

    urlpatterns += patterns(
        '',
        url(r'^api/', include(ROUTER.urls)),
        url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    )

# If hosting sparkle updates include the urls.
if settings.HOST_SPARKLE_UPDATES:
    urlpatterns += patterns(
        '',
        url(r'^sparkle/', include('sparkle.urls'))
    )

## Heroku deployment static files
if 'DYNO' in os.environ:
    urlpatterns += patterns(
        '',
        # static files
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)

# All Other depolyments
elif not settings.RUNNING_ON_APACHE:
    if  settings.SERVE_FILES or settings.HOST_SPARKLE_UPDATES:
        urlpatterns += patterns(
            '',
            # static files
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
            url(r'^files/private/*', RedirectView.as_view(url=u'/%s', permanent=False), name='nowhere'),
            url(r'^files/(?P<path>.*)$' , 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# Add the empty pattern include now that all other patterns are added.
urlpatterns += patterns(
    '', url(r'^', include('printers.urls'), name='printers'),
)
