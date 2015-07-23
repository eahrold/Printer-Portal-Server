##Configure with Docker and Composer
Spinning up a docker container is the simplest way to test out the Printer Portal Server

### Install Docker and Docker Compose
If you don't have docker & docker-compose installed visit the site and get going https://docs.docker.com/compose/install
	
### Clone and configure
Grab the Printer Portal Server from github , `cd` into the  location you keep your code, then clone repo

```
cd ~/code 

git clone https://github.com/eahrold/Printer-Portal-Server.git printer_portal

cd printer_portal

```

Next make a copy of the settings_template.py
```
cp printer_portal/settings_template.py printer_portal/settings.py
```

Now you'll want to edit this file and change some of the settings. you'll at least want to modify these two keys

1. `SECRET_KEY`
2. `ORGANIZATION_NAME`

Here's a good way to generate a secret key [From Here](http://techblog.leosoto.com/django-secretkey-generation/)
```
python -c 'import random; import string; print "".join([random.SystemRandom().choice(string.digits + string.letters + string.punctuation) for i in range(100)])'
```

### Run the Dockerfile & SyncDB 
	```
	docker-compose build
	docker-compose run web python manage.py syncdb
	
	```

### Start the app

	```
	 docker-compose up
	```

### Done
Goto http://localhost:8000 and poke around.  

_*if you're running boot2docker you'll need to use the ip taken from `boot2docker ip`_

### And rm the containers when you're done testing
```
docker-compose rm
```