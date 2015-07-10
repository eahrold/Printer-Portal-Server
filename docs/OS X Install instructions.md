*please see the README.md at the root of this project for more general instructions.  The app must be setup prior to these configuration steps*

#OS X Setup#

These are examples of how to get this up and running on an OS X Mountian Lion Server and beyond (it should also work for Lion).

You will need to create three files:

-
###1. Apache Conf file
Create the file: `/Library/Server/Web/Config/apache2/httpd_printer_portal.conf`

With contents:
```
# This is the Config file to accompany the os X server webapp
# edu.loyno.smc.printer_portal.webapp.plist,

# if running along side of other webapps and on the same port prefix /printers
# to subpath all of the Aliases/ScriptAliases/Locations
# if running on a single port you can change them to just /
WSGIScriptAlias /printers /Library/Server/Web/Data/webapps/printer_portal.wsgi
Alias /printers/static/ /usr/local/www/printer_portal_env/printer_portal/printer_portal/static/
Alias /printers/files/ /Library/Server/Web/Data/Sites/printer_portal_env/printer_portal/printer_portal/files/

<Location /printers/files/private/>
    Order Allow,Deny
    Deny from  all
</Location>

# Uncomment the section below to isolate the virtual environment, However you must only run on a single
# port if you choose to do this, you can't run on both http and https

# WSGIDaemonProcess printer_portal user=printer_portal group=printer_portal
# <Location /printers>
#     WSGIProcessGroup printer_portal
#     WSGIApplicationGroup %{GLOBAL}
#     Order deny,allow
#     Allow from all
# </Location>

```

-
###2. The webapp.plist
Create the file:
```
/Library/Server/Web/Config/apache2/webapps/com.github.eahrold.printer_portal.webapp.plist
```
With contents:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>displayName</key>
	<string>Printer Portal Server</string>
	<key>includeFiles</key>
	<array>
		<string>/Library/Server/Web/Config/apache2/httpd_printer_portal.conf</string>
	</array>
	<key>installationIndicatorFilePath</key>
	<string>/Library/Server/Web/Data/webapps/printer_portal.wsgi</string>
	<key>launchKeys</key>
	<array/>
	<key>name</key>
	<string>com.github.django.printer_portal.webapp</string>
	<key>requiredModuleNames</key>
	<array>
		<string>wsgi_module</string>
	</array>
</dict>
</plist>

```
-
###3. The WSGI configuration
Create the file
```
/Library/Server/Web/Data/WebApps/printer_portal.wsgi
```

With Contents:  

*_change the `VIR_ENV_DIR` directive below to your virtual environment path_ 

```
import os, sys
import site

#set the next line to your printer_portal environment
VIR_ENV_DIR = '/usr/local/www/printer_portal_env'

# Use site to load the site-packages directory of our virtualenv
site.addsitedir(os.path.join(VIR_ENV_DIR, 'lib/python2.7/site-packages'))

# Make sure we have the virtualenv and the Django app itself added to our path
sys.path.append(VIR_ENV_DIR)
sys.path.append(os.path.join(VIR_ENV_DIR, 'printer_portal'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "printer_portal.settings")
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
```

### After all of the files are installed...

1. Open the Server.app  
2. Go to Websites.
3. Open the website you wish to enable it on  
4. In the advanced tab set "Printer-Portal-Server" to enabled.
