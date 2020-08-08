async function loadData(loadAssign=true, resetTeachers=true){
    resetTeacherState();
    if(resetTeachers){
        await getTeachers();
    }

    timetable.deleteAllEvents();
    timetable.deleteAllBlocks();
    await getBlocks();


    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    timetable.setDays(new Date(startDate));

    await getHolidays(startDate, endDate);
    await getStages(startDate, endDate);
    if(loadAssign)
        await getAssignments(startDate, endDate);
}

async function loadTeacherData(){
    timetable.deleteAllEvents();
    timetable.deleteAllBlocks();
    await getBlocks();

    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    timetable.setDays(new Date(startDate));

    await getHolidays(startDate, endDate);
    await getTeacherAssignments(startDate, endDate);
}

async function loadRoomData(){
    timetable.deleteAllEvents();
    timetable.deleteAllBlocks();
    await getBlocks();

    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    timetable.setDays(new Date(startDate));

    await getHolidays(startDate, endDate);
    await getRoomAssignments(startDate, endDate);
}

async function goNextWeek(teacher=false, room=false){
    currentDate = moment(currentDate).add(7, 'days').toDate();
    if(teacher)
        await loadTeacherData();
    else if(room)
        await loadRoomData();
    else
        loadData();
}
async function goPrevWeek(teacher=false, room=false){
    currentDate = moment(currentDate).subtract(7, 'days').toDate();
    if(teacher)
        await loadTeacherData();
    else if(room)
        await loadRoomData();
    else
        loadData();
}

function addExtraBlock(){
    let date = moment(currentDate).add($('#day_of_week').val(), 'days').toDate();
    let hourStart = $('#hour_start').val();
    let hourEnd = $('#hour_end').val();
    let block = createExtraBlock(date, hourStart, hourEnd, true);
    $('#modalExtraLecture').modal('hide');
}

function resetTeacherState(){
    for(let tea of $('#teachers_list').children()){
        $(tea).removeClass('active');
    }
}

function parseStringTime(time){
    let arr = time.split(':');
    let hours = parseInt(arr[0]);
    let min = parseInt(arr[1]);
    return { hours: hours, min: min };
}
function formatStringTime(time){
    let frm = (x) => ("0" + x).slice(-2);

    let hours = frm(time.hours);
    let min = frm(time.min);
    return hours + ":" + min;
}
function formatDate(date){
    if(date === undefined)
        return date;

    let frm = (x) => ("0" + x).slice(-2);
    return date.getFullYear() + "-" + frm(date.getMonth() + 1) + "-" + frm(date.getDate());
}

function extraBlockExists(date, hourStart, hourEnd){
    let starts_at = parseStringTime(hourStart);
    let ends_at = parseStringTime(hourEnd);
    let day_of_week = moment(date).day() - 1;
    let blockId = day_of_week + hourStart + hourEnd;

    let block = timetable.getBlock(blockId);
    return block !== undefined;
}
function createExtraBlock(date, hourStart, hourEnd, deletable=false){
    let starts_at = parseStringTime(hourStart);
    let ends_at = parseStringTime(hourEnd);
    let day_of_week = moment(date).day() - 1;
    let blockId = day_of_week + hourStart + hourEnd;

    let block = timetable.getBlock(blockId);
    if(block === undefined){
        block = new Block(blockId, _TRANS['extra_block_title'], day_of_week, starts_at, ends_at, deletable);
        timetable.addBlock(block);
    }
    return block;
}
async function getBlocks(){
    let url = _URL['hour_slot'];
    let data = {
        'school_year': $('#school_year').val()
    };
    try{
        data = await $.get(url, data=data);
        for(let slot of data){
            let starts_at = parseStringTime(slot.starts_at);
            let ends_at = parseStringTime(slot.ends_at);

            let block = new Block(slot.id, slot.hour_number + _TRANS['lecture_title'], slot.day_of_week, starts_at, ends_at);
            timetable.addBlock(block);
        }
    }
    catch{
        console.log("No blocks");
    }
}
async function getClassYears(){
    let url = _URL['year_only_course'];
    let data = {
        'school_year': $('#school_year').val()
    };
    $('#course_year').empty();
    try{
        data = await $.get(url, data=data);
        for(let year of data){
            $('#course_year').append(`<option value="${year.year}">${year.year}</option>`);
        }

        //update section select
        await getClassSections();
    }
    catch{
        console.log("No classYear");
    }
}
async function getClassSections(){
    let url = _URL['section_only_course'];
    let data = {
        'school_year': $('#school_year').val(),
        'year': $('#course_year').val()
    };
    $('#course_section').empty();
    try{
        data = await $.get(url, data=data);
        for(let sect of data){
            $('#course_section').append(`<option value="${sect.id}">${sect.section}</option>`);
        }

        $('#course_section').change();
    }
    catch{
        console.log("No classSection");
    }
}

async function getTeachers(){
    let url = _URL['hour_per_teacher_in_class'];
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val()
    };
    $('#teachers_list').empty();
    try{
        data = await $.get(url, data=data);
        for(let tea of data){
            let html = `
                <li class="list-group-item list-teachers" data-teacher-id="${tea.id}">
                    <div class="row">
                        <div class="col-10">
                            <b>${tea.teacher.last_name} ${tea.teacher.first_name}</b> - ${tea.subject.name}
                        </div>
                        <div class="col-2 p-0">
                            <button class="btn btn-link text-right" style="color: inherit" data-toggle="collapse" data-target="#tea-collapse-${tea.id}" aria-expanded="true" aria-controls="tea-collapse-${tea.id}">
                                <svg class="bi bi-caret-down-fill" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M7.247 11.14L2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"/>
                                </svg>
                            </button>
                        </div>                        
                    </div>
                     
                    <div id="tea-collapse-${tea.id}" class="collapse">
                        <div class="row font-italic">
                            <span class="col-9">${_TRANS['hours_teaching']}:</span>
                            <span class="col-3 tea-hours">${tea.hours}</span>
                        </div>
                        <div class="row font-italic">
                            <span class="col-9">${_TRANS['hours_bes']}</span>
                            <span class="col-3 tea-hours_bes">${tea.hours_bes}</span>
                        </div>
                        <div class="row font-italic">
                            <span class="col-9">${_TRANS['hours_co-teaching']}</span>
                            <span class="col-3 tea-hours_bes">${tea.hours_co_teaching}</span>
                        </div>
                        <hr/>
                        <div class="row font-italic">
                            <span class="col-9">${_TRANS['missing_hours']}:</span>
                            <span class="col-3 tea-missing_hours">${tea.missing_hours}</span>
                        </div>
                        <div class="row font-italic">
                            <span class="col-9">${_TRANS['hours_bes']}</span>
                            <span class="col-3 tea-missing_bes">${tea.missing_hours_bes}</span>
                        </div>
                        <div class="row font-italic">
                            <span class="col-9">${_TRANS['hours_co-teaching']}</span>
                            <span class="col-3 tea-missing_bes">${tea.missing_hours_co_teaching}</span>
                        </div>
                    </div>
                    <div class="row">
                        <button type="button" class="col-6 btn btn-sm cal-event" onclick="teacherClick($(this).parent().parent(), ${tea.id}, ${tea.teacher.id}, ${tea.subject.id}, ${tea.school}, false, false)">${_TRANS['assign_lecture']}</button>
                        <button type="button" class="col-6 btn btn-sm cal-event-bes" onclick="teacherClick($(this).parent().parent(), ${tea.id}, ${tea.teacher.id}, ${tea.subject.id}, ${tea.school}, true, false)">${_TRANS['assign_bes']}</button>
                        <button type="button" class="col-12 btn btn-sm cal-event-co-teaching mt-1" onclick="teacherClick($(this).parent().parent(), ${tea.id}, ${tea.teacher.id}, ${tea.subject.id}, ${tea.school}, false, true)">${_TRANS['assign_co-teaching']}</button>
                    </div>
                </li>`;
            $('#teachers_list').append(html);
        }
    }
    catch{
        console.log("No teachers");
    }
}

async function refreshTeachers(){
    let url = _URL['hour_per_teacher_in_class'];
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val()
    };
    try{
        data = await $.get(url, data=data);
        for(let tea of data){
            let teaElement = $(`#teachers_list *[data-teacher-id=${tea.id}]`);

            teaElement.find('.tea-hours').text(tea.hours);
            teaElement.find('.tea-hours_bes').text(tea.hours_bes);
            teaElement.find('.tea-missing_hours').text(tea.missing_hours);
            teaElement.find('.tea-missing_bes').text(tea.missing_bes);
        }
    }
    catch{
        console.log("No teachers");
    }
}

async function getAssignmentsGeneric(url, startDate, endDate){
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    timetable.deleteAllEvents();
    try{
        data = await $.get(url, data=data);
        for(let assign of data){
            let blockId = assign.hour_slot;
            if(blockId === null){
                blockId = createExtraBlock(assign.date, assign.hour_start, assign.hour_end).id;
            }

            let teacher = assign.teacher.first_name + " " + assign.teacher.last_name;
            let subject = assign.subject.name;
            if (assign.room)
                subject = `
                <svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-tag-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M2 1a1 1 0 0 0-1 1v4.586a1 1 0 0 0 .293.707l7 7a1 1 0 0 0 1.414 0l4.586-4.586a1 1 0 0 0 0-1.414l-7-7A1 1 0 0 0 6.586 1H2zm4 3.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/>
                </svg> ` + subject;
            let customEvent = new Event(assign.id, teacher, subject);
            let clickEvent = (event) => {
                alert("Lecture " + assign.subject.name + ", teacher " + event.teacher);
            };
            timetable.addEvent(customEvent, blockId, clickEvent, deleteAssignment);

            if(assign.bes){
                customEvent.htmlElement.addClass('cal-event-bes');
            }
            else if(assign.co_teaching){
                customEvent.htmlElement.addClass('cal-event-co-teaching');
            }
            else if(assign.absent){
                customEvent.htmlElement.addClass('cal-event-absent');
            }
            else if(assign.substitution){
                customEvent.htmlElement.addClass('cal-event-substitution');
            }

            let lbl_room = '';
            if (assign.room)
                lbl_room = 'Room: ' + assign.room.name;
            customEvent.htmlElement.tooltip({
                title: `
                    <b>${teacher}</b><br/>
                    ${assign.subject.name}<br/>
                    ${lbl_room}<br/>
                    ${assign.hour_start.slice(0, -3)} - ${assign.hour_end.slice(0, -3)}
                `,
                html: true,
                boundary: 'window'
            })
        }
    }
    catch{
        console.log("No assignments");
    }
}

async function getAssignments(startDate, endDate){
    let url = _URL['assignments'];
    await getAssignmentsGeneric(url, startDate, endDate);
}

async function getTeacherAssignments(startDate, endDate){
    let url = _URL['teacher_timetable'];
    await getAssignmentsGeneric(url, startDate, endDate);
}

async function getRoomAssignments(startDate, endDate){
    let url = _URL['room_timetable']
        .replace('1234', $('#room').val());
    await getAssignmentsGeneric(url, startDate, endDate);
}

async function getHolidays(startDate, endDate){
    let url = _URL['holiday'];
    let data = {
        'school_year': $('#school_year').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    try{
        data = await $.get(url, data=data);
        for(let day of data){
            let start = moment(day.start);
            let end = moment(day.end);
            while(start <= end) {
                timetable.lockDay(start.weekday() - 1, day.name);
                start.add(1, 'days');
            }
        }    
    }
    catch{
        console.log("No holidays");
    }
}
async function getStages(startDate, endDate){
    let url = _URL['stage'];
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    try{
        data = await $.get(url, data=data);
        for(let day of data){
            let start = moment(day.start);
            let end = moment(day.end);
            while(start <= end) {
                timetable.lockDay(start.weekday() - 1, day.name);
                start.add(1, 'days');
            }
        }
    }
    catch{
        console.log("No stages");
    }
}

async function teacherClick(btn, teaId, teacherId, subjId, schoolId, bes, co_teaching){
    btn = $(btn);

    if(!btn.hasClass('active')){
        $('#teachers_list li').removeClass('active');
        btn.addClass('active');

        for(let blk of Object.keys(timetable.blocks)){
            timetable.getBlock(blk).setState('available');
            timetable.getBlock(blk).setOnClick((blk) => chooseAssignmentRoom(teaId, teacherId, subjId, schoolId, blk, bes, co_teaching));
        }

        await setLockedBlocksTeacher(teacherId);
        await setLockedBlocksAbsenceTeacher(teacherId);
    }
    else{
        btn.removeClass('active');

        timetable.resetAllBlocksStates();
    }
}

async function setLockedBlocksTeacher(teacherId){
    let school_year = $('#school_year').val();
    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    let url = _URL['teacher_assignments']
        .replace("12345", teacherId).replace("99999", school_year);
    let data = {
        'school_year': school_year,
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    try{
        data = await $.get(url, data=data);
        for(let block of data){
            let blockId = block.hour_slot;
            let create = true;
            if(blockId === null){
                if(!extraBlockExists(block.date, block.hour_start, block.hour_end))
                    create = false; 
            }

            if(create){
                timetable.getBlock(blockId).setState('conflict');
                timetable.getBlock(blockId).setOnClick();
            }
        }    
    }
    catch{
        console.log("No locked blocks for teacher");
    }
}

async function setLockedBlocksAbsenceTeacher(teacherId){
    let school_year = $('#school_year').val();
    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    let url = _URL['teacher_absence_blocks']
        .replace("12345", teacherId).replace("99999", school_year);
    let data = {
        'school_year': school_year,
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    try{
        data = await $.get(url, data=data);
        for(let block of data){
            let blockId = block.hour_slot;
            let create = true;
            if(blockId === null){
                if(!extraBlockExists(block.date, block.hour_start, block.hour_end))
                    create = false; 
            }

            if(create){
                timetable.getBlock(blockId).setState('absence');
                timetable.getBlock(blockId).setOnClick();
            }
        }    
    }
    catch{
        console.log("No absence blocks for teacher");
    }
}

async function chooseAssignmentRoom(teaId, teacherId, subjId, schoolId, block, bes, co_teaching){
    //get free rooms without conflicts
    let url = _URL['room'];
    let date = moment(currentDate).add(block.day, 'days').format('YYYY-MM-DD');
    let data = {
        school_year: $('#school_year').val(),
        school: schoolId,
        date: date,
        course: $('#course_section').val(),
        hour_start: block.startTime.hours + ':' + block.startTime.min,
        hour_end: block.endTime.hours + ':' + block.endTime.min
    };
    let rooms = await $.get(url, data=data);
    $('#roomSelect').html(`
        <option value="">${_TRANS['no_room']}</option>
    `);
    for(let room of rooms){
        $('#roomSelect').append(`
            <option value="${room.id}">${room.name}</option>
        `);
    }

    $('#btn-room-add-assignment').unbind("click");
    //attach click event to the confirmation button
    $('#btn-room-add-assignment').click(() => {
        addAssignment(teaId, teacherId, subjId, schoolId, block, bes, co_teaching)
    });

    //show the modal
    $('#modalChooseRoom').modal('show');
}
async function addAssignment(teaId, teacherId, subjId, schoolId, block, bes, co_teaching){
    let url = _URL['assignments'];

    let date = moment(currentDate).add(block.day, 'days').format('YYYY-MM-DD');
    let data = {
        csrfmiddlewaretoken: Cookies.get('csrftoken'),
        teacher_id: teacherId,
        course_id: $('#course_section').val(),
        room_id: $('#roomSelect').val(),
        subject_id: subjId,
        school_year: $('#school_year').val(),
        school: schoolId,
        date: date,
        hour_start: block.startTime.hours + ':' + block.startTime.min,
        hour_end: block.endTime.hours + ':' + block.endTime.min,
        bes: bes,
        co_teaching: co_teaching,
        substitution: false,
        absent: false
    };
    try{
        let res = await $.post(url, data=data);
        await loadData(true, false);
        await refreshTeachers();
        await teacherClick($(`#teachers_list *[data-teacher-id=${teaId}]`), teaId, teacherId, subjId, schoolId, bes);
    }
    catch(e){
        console.log("Error adding an assignment");
        console.error(e);
    }
    $('#modalChooseRoom').modal('hide');
}

function deleteAssignment(assign){
    assign.htmlElement.tooltip('hide');
    let res = confirm(_TRANS['delete_lecture_msg']);
    if(res){
        let params = {
            'from_date': formatDate(currentDate),
            'to_date': formatDate(moment(currentDate).add(6, 'days').toDate())
        };
        let url = _URL['assignments'] + assign.id + "?" + $.param(params);
        $.ajax({
            url: url,
            type: 'DELETE',
            beforeSend: function(xhr) {
                xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
            },
            success: function(result) {
                console.log(result, "OK");
                getTeachers();
            }
        });
    }
    return res;
}

async function checkReplicateWeek(){
    let startDate = moment($('#date_start').val(), "DD/MM/YYYY").toDate();
    let endDate = moment($('#date_end').val(), "DD/MM/YYYY").toDate();

    let url = _URL['check_week_replication']
        .replace("0000-00-00", formatDate(startDate))
        .replace("9999-99-99", formatDate(endDate));
    let data = {
        csrfmiddlewaretoken: Cookies.get('csrftoken'),
        assignments: []
    }
    for (let block of Object.keys(timetable.blocks)){
        for(let event of timetable.getBlock(block).events){
            data.assignments.push(event.id);
        }
    }

    let res = await $.post(url, data=data);

    let resultBox = $("#replicateResult");
    resultBox.empty();
    resultBox.append(`
        <b>${_TRANS['teacher_conflicts']}:</b>
        <span class="badge badge-pill ${res.teacher_conflicts.length > 0 ? 'badge-danger' : 'badge-success'}">
            ${res.teacher_conflicts.length}
        </span>
        <ul class="list-group" id="teacher-conflicts">
        </ul>
        <b>${_TRANS['course_conflicts']}:</b>
        <span class="badge badge-pill ${res.course_conflicts.length > 0 ? 'badge-danger' : 'badge-success'}">
            ${res.course_conflicts.length}
        </span>
        <ul class="list-group" id="course-conflicts">
        </ul>
        <b>${_TRANS['room_conflicts']}:</b>
        <span class="badge badge-pill ${res.room_conflicts.length > 0 ? 'badge-danger' : 'badge-success'}">
            ${res.room_conflicts.length}
        </span>
        <ul class="list-group" id="room-conflicts">
        </ul>
    `);

    let teacherConflicts = resultBox.find('#teacher-conflicts');
    let courseConflicts = resultBox.find('#course-conflicts');
    let roomConflicts = resultBox.find('#room-conflicts');

    for(let conflict of res.teacher_conflicts){
        teacherConflicts.append(`
            <li class="list-group-item">
                <b>${conflict.teacher.first_name} ${conflict.teacher.last_name}</b> - ${conflict.subject.name}<br/>
                ${moment(conflict.date).format('DD-MM-YYYY')} 
                <b>${conflict.course.year} ${conflict.course.section}</b>
                ${conflict.hour_start.substring(0,5)} - ${conflict.hour_end.substring(0,5)}
            </li>`);
    }

    for(let conflict of res.course_conflicts){
        courseConflicts.append(`
            <li class="list-group-item">
                <b>${conflict.teacher.first_name} ${conflict.teacher.last_name}</b> - ${conflict.subject.name}<br/>
                ${moment(conflict.date).format('DD-MM-YYYY')} ${conflict.hour_start.substring(0,5)} - ${conflict.hour_end.substring(0,5)}
            </li>`);
    }

    for(let conflict of res.room_conflicts){
        roomConflicts.append(`
            <li class="list-group-item">
                <b>${conflict.room.name} [${conflict.room.capacity}] - ${conflict.teacher.first_name} ${conflict.teacher.last_name}</b> - ${conflict.subject.name}<br/>
                ${moment(conflict.date).format('DD-MM-YYYY')}
                <b>${conflict.course.year} ${conflict.course.section}</b>
                ${conflict.hour_start.substring(0,5)} - ${conflict.hour_end.substring(0,5)}
            </li>`);
    }
}

async function replicateWeek(){
    let startDate = moment($('#date_start').val(), "DD/MM/YYYY").toDate();
    let endDate = moment($('#date_end').val(), "DD/MM/YYYY").toDate();

    let url = _URL['replicate_week']
        .replace("12345", $('#school_year').val())
        .replace("99999", $('#course_section').val())
        .replace("0000-00-00", formatDate(startDate))
        .replace("9999-99-99", formatDate(endDate));
    let data = {
        csrfmiddlewaretoken: Cookies.get('csrftoken'),
        assignments: []
    }

    for (let block of Object.keys(timetable.blocks)){
        for(let event of timetable.getBlock(block).events){
            data.assignments.push(event.id);
        }
    }

    try {
        let res = await $.post(url, data=data);
        $('#modalReplicateWeek').modal('hide');
        alert(_TRANS['week_replicated_msg']);
    }
    catch(e){
        if(e.status === 400){
            let results = e.responseJSON;
            let dates = '';
            for(let d of results){
                dates += d.date + ', ';
            }
            alert(_TRANS['conflict_dates_msg'] + " " + dates);
        }
    }
}
