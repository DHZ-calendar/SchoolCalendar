# SchoolCalendar
![Django CI](https://github.com/DHZ-calendar/SchoolCalendar/workflows/Django%20CI/badge.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar/badge)](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar)

## Traduzione in Italiano
[Traduzione in Italiano](#Italian-translation)

## Presentation
We know how hard is the process of creating the calendar of a school: all classes cannot be left without a teacher, still no teacher can be assigned to multiple classes at the same time - unless time travel were possible, but this is definitely another story ;). And moreover, at the end of the year all teachers must have done their yearly amount of hours per class. And what if some teacher substitutions were necessary during the year due to illness? It's a nightmare!

But no worry, we may have made your life much easier: SchoolCalendar helps you to create the calendar for your school! 

This website allows you to keep track of teachers', classes' and rooms' availability in your school, so that no conflict is made while you create the timetable. If you are the admin for the school, an interactive page lets you build the timetable, whereas all teachers can see their weekly load by checking their personal account. Moreover, there is the possibility to manage the dinamic substitutions of teachers that happen often during the year, and you can keep track of how many hour every teacher is missing to reach their target by visualizing annual reports.

Next sections will present you a comprehensive guide on how to install it and how to operate when you have the service up and running.

Do you want to give it a try? You can check the DEMO available at the website `https://schoolcalendardemo.herokuapp.com` (poor performance are mainly due to the scarsity of resources for the demo freemium service. When installed properly, you should experience a much smoother usability).

Let us now start!

## User Guide

### Initialization

You are the headmaster of a school, and have obtained a valid account's credentials (yay!): what do you need to do now?

Well first of all open a browser (we highly discourage you to use whichever version of IE), type the website URL and login.

You should see something like:

![Home Empty](readme_pics/home_empty.png)

Now open the menu at the upper left corner, click the `Admin` button, open the instance you want to edit (like `Teacher`) and start adding the objects you will need to have the service working (using the button `+ Add new`). We make a brief tour of them:

- Teacher: the teachers in your school. For every teacher an account will be created, so that the teacher in question will be able to consult his own timetable whenever she wises. The ```username``` is the login credential (so choose it carefully, no spaces are available). The `email` address that you insert will receive soon an email by the website, so that every teacher can choose her own password and finish the registration (you will not need her to finish the registration, the Teacher will be usable in the system as soon as you create it)!
- Course: for instance, class IA or whatever. The field `Year` is a number (not Roman!) for the year of the class (in our example, class IA has `Year` field set to 1). The section would instead be `A`. 
- Room: for maximal flexibility, you can optionally register into the system all the rooms of your school. In this way, you can keep track of the conflicts happening in the rooms (the same room cannot be used concurrently by too many courses). Watch out, the field `Capacity` does not stand for how many pupils can fit into the room, but how many courses can be there concurrently (imagine a large laboratory or the gym, we may have multiple courses all having class there at the same time). We still expect that the vast majority of the rooms will have capacity of 1.
- Subject: the subjects taught in the school (Maths, Literature and so on).
- Holiday: you do not want your poor teachers and pupils to work at Christmas ;) The holiday period specified will be valid for all the courses of the school! Try to insert one, you will see it painted in orange in the home page calendar!
- Stage: same as holiday (no class can be held if there is a stage that day), but this time it is specific for a single course.
- Hour Slot: this is the slot in which a lesson can be taught. For instance, assume that on Tuesday the third hour goes from 11:05 to 11:55. Then the field `Hour number` is 3. Still, when you count how many hours a teacher has done during the year, you may want to count the class duratoin as 1 hour, even if it lasts only 50 minutes (after 6 classes of 50 minutes, the teacher has done actually only 5 hours!). This is what the `Legal Duration` field is for! (You can set it with hours and minutes, but we believe that the vast majority will be 1 hour and 0 minutes). This insertion is going to be a bit painful since you may have potentially 30 or more hour slots in a week! But bring a little bit of patience, you have to do insert them only once! ;)
- Absence Block: if any teacher has some chronical indisposability to teach in certain hour slots, you can register them using the `Absence Block`. When you later check for the disposability of a teacher to teach in a certain course, such hour slot will not be considered valid, even if the teacher has no other conflicts at such time.
- Hours Per Teacher In Class: this records how many hours of teaching (field `Hours`) any teacher needs to do in every course. Note that when computing the total amount of hours done by the teacher in a course, the field `Legal Duration` of the instance `Hour Slot` is used). If a teacher teaches multiple subjects in the same course (like Physics and Maths), she needs multiple Hours Per Teacher In Class (one for Math, the other for Physics in the example). The `Hour BES` field is meant for special hours of teaching (like hours done with pupils carrying disability and so on). If your school does not have such special hours, just leave them set to zero.

Fill these fields carefully! All the information that you provide to the website must be correct, or it will work (of course) in an unexpected manner!

### Teachers' Assignments
Now that we have done the initialization step, we can finally start to use the service! We guide you in the next subsection.

FILL THIS!


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
You will have to play with the settings.py file too, in order to setup your Database (Postgresql is our choice, but you can have whatever you wish, and an sqlite3 DB comes out of the box), and of course be careful not to disclose your credentials!

Lastly, you have to setup an email that our website uses to invite teachers to join the service. 

## Italian Translation
Ancora da fare!

## How to contribute
### Update translations
- Update the .po files executing:
```
python manage.py makemessages
```
- Edit the translations in the *.po files 
- Compile the translation files executing:
```
django-admin compilemessages
```
