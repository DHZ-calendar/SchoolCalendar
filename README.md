# SchoolCalendar
![Django CI](https://github.com/DHZ-calendar/SchoolCalendar/workflows/Django%20CI/badge.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar/badge)](https://www.codefactor.io/repository/github/dhz-calendar/schoolcalendar)

## [Traduzione in Italiano 🇮🇹](README_IT.md)

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
- Hour Slot: this is the slot in which a lesson can be taught. For instance, assume that on Tuesday the third hour goes from 11:05 to 11:55. Then the field `Hour number` is 3. Still, when you count how many hours a teacher has done during the year, you may want to count the class duratoin as 1 hour, even if it lasts only 50 minutes (after 6 classes of 50 minutes, the teacher has done actually only 5 hours!). This is what the `Legal Duration` field is for! (You can set it with hours and minutes, but we believe that the vast majority will be 1 hour and 0 minutes). This insertion is going to be a bit painful since you may have potentially 30 or more hour slots in a week! But do not worry, we saved you a bunch of time by letting you decide in which days of the week to repeat the hour slot. For instance, if you want the first hour of the morning from 8:00 to 9:00 to be repeated every morning from Monday to Friday, just select the correct days in the field `Replicate on Days`. In order to select multiple options use the key `ctrl`, or `shift`.
- Absence Block: if any teacher has some chronical indisposability to teach in certain hour slots, you can register them using the `Absence Block`. When you later check for the disposability of a teacher to teach in a certain course, such hour slot will not be considered valid, even if the teacher has no other conflicts at such time.
- Hours Per Teacher In Class: this records how many hours of teaching (field `Hours`) any teacher needs to do in every course. Note that when computing the total amount of hours done by the teacher in a course, the field `Legal Duration` of the instance `Hour Slot` is used). If a teacher teaches multiple subjects in the same course (like Physics and Maths), she needs multiple Hours Per Teacher In Class (one for Math, the other for Physics in the example). The `Hour BES` field is meant for special hours of teaching (like hours done with pupils carrying disability and so on). If your school does not have such special hours, just leave them set to zero.

Fill these fields carefully! All the information that you provide to the website must be correct, or it will work (of course) in an unexpected manner!

### An example creation of entries 
Now that we have done the initialization step, we can finally start to use the service! We guide you through this process in this subsection.

For the sake of the example, we just created a School Admin account (the same type of account that you are using right now) called John Doe, who is the manager of the school called "Galilei High School". You cannot create nor a school nor a school_year with your current account: you have to ask the administrators (the same guys who created for you your account) of the website to add your `school` and the `school_year` to the system!

Now that we have everything up and running we start to fill what is necessary in order to utilize properly the website: let us start by the basis, and insert some hour-slots. Open the left menu, click the `Admin` option and select `Hour-Slots`. Add a new one and fill it as you wish. (Note that in this case the hour lasts physically speaking only 50 minutes, but the legal duration makes sure that it is going to be counted as a full hour long lesson). We insert both the hour slot for the first hour (7.55-8.45) and the second hour (8.45-9.35)

![HourSlotCreate](readme_pics/HourSlotInsertion.png)

You can check that the insertion was successful by going back to the home page (left menu -> Timetable), and see that the hourslots appear in a gray overlay on the timetable.

![TimetableWithHourslots](readme_pics/timetable_with_hourslots.png)

We now insert a few courses (1A, 2A, 3A, 4A, 5A): go to left menu -> Admin -> Courses -> Add new, and fill the forms with the information for the various courses (careful, if the course is 1A, then the year is 1 - it must be a number - and the section is A). For example:

![CourseCreation](readme_pics/Course_creation.png)

We now insert some subjects (left menu -> Admin -> Subjects -> Add New): Maths, Physics, Italian Literature, English Literature.

Let us now insert a few rooms: you do not need to insert all of them (although you are not prohibited either from doing so), but just the ones you believe will be likely to have conflicts (for instance, the laboratories that can be used by multiple courses).

In order to add some rooms go to left menu -> Admin -> Rooms -> Add new. We create a couple of rooms, the Physics laboratory (with capacity 2, which means that can be used concurrently by two courses and not that it can fit only two students) and the Multimedia Laboratory (with capacity 1).

![RoomCreation](readme_pics/rooms_creation.png)

It is time to add some teachers: go to left menu -> Admin -> Teachers -> Add new, and create a few teachers. We are going to create for this example the teachers Marie Curie, Dante Alighieri, Oscar Wilde and Carl Friedrich Gauss. 

Note that: the `username` field is going to be the username that the teacher will use use in order to login - choose it carefully, there cannot be duplicates and it cannot contain spaces! The email is instead required since the teacher is going to receive an email from SchoolCalendar, so that she can set her own password (she will use the account to check her personal timetable, she will not be able to alter anything since she is not an admin as you are!). The email is not sent automatically: you need to click the button `Send Invite` in the page left menu -> Admin -> Teachers.

![TeacherCreate](readme_pics/teacher_create.png)

We create now an absence block: our poor Dante cannot be present at school from 8:00 to 9:00 on Mondays, since he has to take care of his old friend Virgilio. Just go to left menu -> Admin -> Absence Blocks -> Add new, and fill the form with Dante's information.

![AbsenceBlockCreation](readme_pics/absence_block_create.png)

Now we insert the important information regarding the teachers and courses: how many hours does every teacher need to teach in every course. To keep things simple, we just say that every teachers in our example teaches her own subject (we do not need to explain who teaches what, right?) in courses 1A and 2A. For the sake of the simplicity of the example, we just assign 100 normal hours to every teacher in every course, apart from Dante in 1A, who teaches both 100 normal hours and 50 BES.

![HourPerTeacherInClass](readme_pics/hour_per_teacher_in_class_create.png)

Lastly, we insert some holidays and some stages. First, go to left menu -> Admin -> Holidays -> Add new and create a new holiday: 

![HolidayCreate](readme_pics/holiday_create.png)

Then a stage for class 1A: left menu -> Admin -> Stages -> Add new.

![StageCreate](readme_pics/stage_create.png)

You can check how those two instances are rendered in the timetable: go to left menu -> Timetable, go to the desired week using the button `go`, right above the timetable (for the stage and the holiday), and look for them, they should be fairly easy to spot.

### Teacher Assignment

After we have finished to set all the entries of our mock school, we can finally start to see how the system works. Go to the timetable page (left menu -> Timetable) and start to play with the teachers assignments.
This view shows you the weekly timetable for a specific course and school year (you can select which course and school year to visualize in the upper left menu). Note that the list of teachers in the right column will change according to the course you have selected. If you try to select course 3A, for instance, you will notice that it has no teacher assigned (if you remember, we only add hours for teachers in courses 1A and 2A).

Try now to add an Italian lecture the second hour on Monday in course 1A. Click the button `Assign lecture` in Dante's square, and afterwards select the first hour slot on Monday morning (it should have been filled in green).

![AssignButton](readme_pics/Assign_teacher.png)

It will be asked whether you want to assign a room to this lecture, to which you can say `No Room`.

![NoRoomAddLecture](readme_pics/No_room_add_lecture.png)


What about the first hour slot? Why is it still gray and it doesn't turn into green? Simple enough, Dante is by Virgilio's, we have added an absence block for him at that time.

So good so far: let us now add a Math class during the first hour slot on Monday morning. Just repeat the same procedure with Gauss: notice that when you press the button `Assign lecture` under Gauss' square, the Italian lecture we added earlier will appear split in half: this is to let you add more than one teacher during the same course.

![HourSlotSplit](readme_pics/Hour_Slot_split.png)

Before starting to add courses in the other course, try to click the downward arrow in the teachers' box in the right column: it will show you a summary of how many hours does the teacher still need to do in the course.

Ok, move on right now in class 2A (using the menu at the top left corner). Try to add a lecture for Dante; as you can see, Monday is off limits: first hour Dante is as usual by Virgilio, second hour instead there would be a conflict with course 1A. It is shown in red.

![ConflictRedHourSlot](readme_pics/conflict_red_hour_slot.png)

Add him then during the first hour slot on Tuesday, and add him in the Multimedia Laboratory. If you go back to class 1A, and try to add another teacher (Oscar Wilde) in the same hour slot in the same room, you can notice that you cannot! (The multimedia laboratory won't appear as one of the possible options when choosing the room). Which makes sense, in fact the multimedia laboratory has capacity only one.

If you now add instead a lecture for Marie Curie in the Physics laboratory in course 1A, the second hour of Tuesday, and then do the same for course 2A, putting Gauss in the physics laboratory as well, you notice that you can! The Physics lab can hold concurrently 2 classes together (we created it with capacity 2).

To recap what we have done so far, here is a picture of the classes that we have assigned until now for courses 1A and 2A.

![hourscourse1a](readme_pics/1a_hours.png)
![hourscourse2a](readme_pics/2a_hours.png)

### Substitution

We explore now another feature of SchoolCalendar: assume it is Monday evening, and Gauss calls you to tell you that he is ill and will not be able to attend the lecture he has in course 2A. You have therefore to find a right candidate for a substitution. Normally you should consider all lectures that Gauss teaches on Tuesday, look for a candidate to substitute him, check for the candidate's conflicts, and repeat the process for all Gauss' lectures of the day: a nightmare. And with SchoolCalendar? Just a piece of cake. 

Open the left menu -> Substitute a teacher, and fill the form with the correct information (Gauss, on the 7th of July). 

![GaussSubstitution](readme_pics/gauss_substitution.png)

As you can notice, a list of all lectures that you need to fill is proposed to you (in our case, only the second hour of Tuesday).

If you click on it, a list of all teachers will open at your disposal

![GaussSubstitution2](readme_pics/substitute_gauss_teacher_list.png)

The information in this page should help you decide who will make the substitution: first, you may want to give the lecture to the teacher with less hours of substitutions made so far during the year. Moreover, you may want to prefer to give the hour to teachers already at school: note for instance that Oscar Wilde is home on Tuesday both the hour before the substitution and the one after, whereas Dante would already be at school (he teaches the hour before Gauss in course 2A). We believe this information will help you to decide to which teacher to assign the substitution.

In the end, Marie Curie is teaching in another class at that hour, hence she will be listed in `Other Teachers` list: you should not choose her, but if you have very good reasons for doing so, feel free (for instance, Marie Curie's class is doing an educational trip, and she is not one of the accompanists).

If we choose Dante, and assign him to the substitution, you will notice in the Timetable page that Gauss is going to be set as absent (purple color) whereas Dante will be set as the substitute (light blue). Good! :)

![SubstitutionInTimetable](readme_pics/substitution_in_timetable.png)



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
