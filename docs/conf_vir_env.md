###If you don't have virtualenv install it
```
sudo easy_install virturalenv
```

###Then create a virtualenv
```
cd /path/to/www/
virtualenv printer_portal_env
```

###Make a user and group
- In linux
	```
	# Set this to where your user homes are stored.
	mkdir -p /home/printer_portal 

	groupadd printer_portal
	
	# set the -u flag to an an appropriate one for your server
	useradd –u 400 –d /home/printer_portal/ –g printer_portal –c “printer_portal” –s /bin/sh

	passwd printer_portal 

	```
- in OSX
	- *Get the last user and group in the 400's,  if this command returns nothing then you can set the UniqueID and GroupID to 400*
 
	```
	USER_ID=$(dscl . list /Users UniqueID | awk '{print $2}'| grep '[4][0-9][0-9]'| sort| tail -1)
	[[ -n $USER_ID ]] && ((USER_ID++)) || USER_ID=400
	
	# should return the next available UID
	
	GROUP_ID=$(dscl. list /Groups PrimaryGroupID | awk '{print $2}'| grep '[4][0-9][0-9]'| sort| tail -1)
	[[ -n $GROUP_ID ]] && ((GROUP_ID++)) || GROUP_ID=400
	
	# that should return the next available GID

	
	# Add the user and group...	
	sudo dseditgroup -o create -n printer_portal -i "$GROUP_ID" -n . printer_portal
sudo dscl . create /Users/printer_portal
sudo dscl . create /Users/printer_portal passwd *
sudo dscl . create /Users/printer_portal UniqueID "$USER_ID"
sudo dscl . create /Users/printer_portal PrimaryGroupID "$GROUP_ID"
	```
	
  
###Fix permissions then switch to new user
```	
sudo chown -R printer_portal printer_portal_env
sudo su ; su printer_portal
```	  
###Turn on the virtual env
	cd printer_portal_env
    source bin/activate
	
###Insatll printer_portal_server
	
	git clone https://github.com/eahrold/printer_portal-server.git printer_portal

###cd into the Directory

	cd printer_portal 

###Install prerequistis

	pip install -r setup/requirements.txt
	
### Configure the app settings

	cd printer_portal
	cp printer_portal/settings_template.py cp printer_portal/settings.py
	
	python manage.py collectstatic
	python manage.py makemigrations
	python manage.py migrate
	python manage.py syncdb
	
During initial testing, in order to server static files,  you'll want to set 
	
	RUNNING_ON_APACHE=False

In the settings.py.  If ultimately running via WSGI module on apache change it back

	RUNNING_ON_APACHE=True

#####There are a few other settings you may wish to change.
* if you want to server PPD files
	```
	SERVE_FILES=True
	```
* if you want to host custom builds of the Printer Portal client app	
	```
	HOST_SPARKLE_UPDATES=True
	```

</br>
### Additional OS X setup
Other tid-bits for OSX Server.app [Setup instructions](./OS X Install instructions.md)