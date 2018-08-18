# akaskhoone server
this repo handles backend of akaskhoone project

## Requirements
* python 3.6
* django 2
* djangorestframework 3

## Setup
#### clone repo
```bash
git clone http://gitlab.rahnemacollege.com/Team-3/akaskhoone.git
```

#### installing ```virtualenv``` if you don't have it already

macOS / Linux:
```bash
pip3 install virtualenv
```
Windows:
```bash
pip install virtualenv
```
#### creating new virtualenv ( macOS / Linux / Windows )
```bash
virtualenv env_akaskhoone
```
#### activate virtualenv with this command

macOS / Linux:
```bash
source env_akaskhoone/bin/activate
```
Windows:
```bash
.\env_akaskhoone\Scripts\activate
```
#### installing requirements

macOS / Linux:
```bash
pip3 install -r akaskhoone/requirements.txt
```
Windows:
```bash
pip install -r akaskhoone/requirements.txt
```

## Migrating
in root directory of project run this command for migrating models

macOS / Linux:
```bash
python3 manage.py migrate
```
Windows:
```bash
python manage.py migrate
```

## Loading Fixture
macOS / Linux:
```bash
python3 manage.py loaddata
```
Windows:
```bash
python manage.py loaddata
```

for profile fixtures remember to copy `profile_photos` directory to media folder too. if you use macOS / Linux in root directory of project run this commands:
```bash
mkdir media
cp -r users/fixtures/profile_photos/ media/
```  

## Runserver
in root directory of project run this command:
> change the ```DEBUG = True``` for testing projext with local Django server. 

macOS / Linux:
```
python3 manage.py runserver
```
Windows:
```
python manage.py runserver
```

and then checkout ```http://127.0.0.1:8000```