from django.conf import settings

def update_server(request):
    return {'update_server': settings.HOST_SPARKLE_UPDATES}

def serve_static(request):
	return {'serve_static': settings.SERVE_FILES}

def app_name(request):
	return {'APP_NAME': settings.APP_NAME}