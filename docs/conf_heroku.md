##Configure with Heroku

### Getting Started
If you don't have a Heroku account sign up for one https://heroku.com

If you don't have the Heroku Toolbelt installed grab that http://toolbelt.herokuapp.com/

### Clone and configure
Grab the Printer Portal Server from github , and `cd` into the  location you keep your code, and clone repo

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

You will also need to remove the settings.py line from the .gitignore file. So open that file, take it out.

### Commit, create & push
```
git add . 
git commit -m "initial heroku commit"
```
If you see a line like this `nothing to commit, working directory clean` make sure you removed the settings.py line from the .gitignore file and add / commit again.

```
heroku create
git push heroku master
heroku run python manage.py syncdb

heroku run python manage.py makemigrations
heroku run python manage.py migrate
```

### Done
```
heroku open
```
