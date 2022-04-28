# SchoolCalendar
![Django CI](https://github.com/DHZ-calendar/SchoolCalendar/workflows/Django%20CI/badge.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar/badge)](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar)


## [User guide](SchoolCalendar/GUIDE.md)

## [Guida utente](SchoolCalendar/GUIDE_IT.md)


## Installation
Two possibilities are there available at the moment: either you download the code (it is an open source repository after all) and start the service by yourself on your school servers, either you pay an annual licence and enjoy the possibility to use the service out of the box on our servers. It will be moreover kept up to date and maintained by our developers! :) The choice is up to you.

If you choose the hard way (installing it by yourself), please know that the software uses the Django backend framework, so be sure to have the possibility to install Python and all the requirements in your server (a php server won't do the job!).

After having cloned the code 
```
git clone https://github.com/DHZ-calendar/SchoolCalendar.git
```
We suggest that you create a virtual environment, where you can install the requirements for our service by typing in a shell (in the same directory of the requirements file)
```
pip install -r requirements.txt
```
You will have to play with the settings.py file too, in order to set up your Database (Postgresql is our choice, but you can have whatever you wish, and an sqlite3 DB comes out of the box), and of course be careful not to disclose your credentials!

Lastly, you have to set up an email that our website uses to invite teachers to join the service. 

## How to contribute
### Update translations
- Update the .po files executing:
```
python manage.py makemessages --all
```
- Edit the translations in the *.po files 
- Compile the translation files executing:
```
django-admin compilemessages
```