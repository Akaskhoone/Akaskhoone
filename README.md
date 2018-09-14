# akaskhoone server
this repo handles backend of akaskhoone project

## Requirements
* python 3.6
* django 2.1
* djangorestframework 3.8
* djangorestframework_simplejwt 3.2.3
* redis 2.10.6
* requests 2.19.1

## Setup
#### clone repo
```
git clone http://gitlab.rahnemacollege.com/Team-3/akaskhoone.git
```
#### installing ```virtualenv``` if you don't have it already
macOS / Linux / Windows:
```
pip install virtualenv
```
#### creating new virtualenv
macOS / Linux / Windows
```
virtualenv env_akaskhoone
```
#### activate virtualenv with this command
macOS / Linux:
```
source env_akaskhoone/bin/activate
```
Windows:
```
.\env_akaskhoone\Scripts\activate
```
#### installing requirements
macOS / Linux / Windows:
```bash
pip install -r akaskhoone/requirements.txt
```
## Migrating
in root directory of project run this command for migrating models

macOS / Linux / Windows:
```bash
python manage.py makemigrations --settings=akaskhoone.settings.base
python manage.py migrate --settings=akaskhoone.settings.base
```

## Loading Fixture
macOS / Linux / Windows:
```bash
python manage.py loaddata user profile tag post board --settings=akaskhoone.settings.base
```
and then:
```bash
mkdir media
cp -r accounts/fixtures/profile_photos media
cp -r social/fixtures/posts media
```  
## Runserver
in root directory of project run this command:
> change the ```DEBUG = True``` for testing projext with local Django server. 

macOS / Linux / Windows:
```
python manage.py runserver --settings=akaskhoone.settings.base
```

and then checkout [127.0.0.1:8000](http://127.0.0.1:8000 "localhost")