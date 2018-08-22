# akaskhoone server
this repo handles backend of akaskhoone project

## Requirements
* python 3.6
* django 2.1
* djangorestframework 3.8
* djangorestframework_simplejwt 

## Contribution Guide
**Please Read this Section Before Contributing**

if you gonna edit any part of code, create new branch for it, with this pattern:

```
S{sprint number}_NameForBranch
```
for example `S1_AddingNewFutureToUser` which is a new branch in sprint 1.

for creating new branch from `master` branch, you can use this command as example. in root directory of project:

```git
git checkout -b S1_NewBranchName master
```

if you commit code related to an issue, provide the issue number in this format:
```
this is the commit message of fixing X issue [TTHREE-102]
```
the `TTHREE-` is what issues are started with in [Jira](http://jira.rahnemacollege.com) for team 3, so follow this rule.

also you can use this tags in comments to make code much more readable too.
also if you use PyCharm you can find these tags by navigating to **`TODO`** panel in bottom:

`todo` could be used to mark something that should be done in future.

`fixme` could be used to notify a problem that must be fixed later.

`snippet` could be used for commented lines of code, that you want to keep them as snippet.

also we use [Semantic Versioning](https://semver.org/), if you don't know how it works, follow the link.

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
#### creating new virtualenv
macOS / Linux / Windows
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
```djangorestframework_simplejwt
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

and then checkout [127.0.0.1:8000](http://127.0.0.1:8000 "localhost")