function loadData(loadAssign=true){
    resetTeacherState();
    getTeachers();

    timetable.deleteAllEvents();
    timetable.deleteAllBlocks();
    getBlocks();


    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    timetable.setDays(new Date(startDate));

    getHolidays(startDate, endDate);
    getStages(startDate, endDate);
    if(loadAssign)
        getAssignments(startDate, endDate);
}

function loadTeacherData(){
    timetable.deleteAllEvents();
    timetable.deleteAllBlocks();
    getBlocks();

    let startDate = currentDate;
    let endDate = moment(startDate).add(6, 'days').toDate();

    timetable.setDays(new Date(startDate));

    getHolidays(startDate, endDate);
    getTeacherAssignments(startDate, endDate);
}

function goNextWeek(teacher=false){
    currentDate = moment(currentDate).add(7, 'days').toDate();
    if(teacher)
        loadTeacherData();
    else
        loadData();
}
function goPrevWeek(teacher=false){
    currentDate = moment(currentDate).subtract(7, 'days').toDate();
    if(teacher)
        loadTeacherData();
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
function getBlocks(){
    let url = _URL['hour_slot'];
    let data = {
        'school_year': $('#school_year').val()
    };
    $.get(url, data=data, function(data) {
        for(let slot of data){
            let starts_at = parseStringTime(slot.starts_at);
            let ends_at = parseStringTime(slot.ends_at);

            let block = new Block(slot.id, slot.hour_number + _TRANS['lecture_title'], slot.day_of_week, starts_at, ends_at);
            timetable.addBlock(block);
        }
    });
}
function getClassYears(){
    let url = _URL['year_only_course'];
    let data = {
        'school_year': $('#school_year').val()
    };
    $('#course_year').empty();
    $.get(url, data=data, function(data) {
        for(let year of data){
            $('#course_year').append(`<option value="${year.year}">${year.year}</option>`);
        }

        //update section select
        getClassSections();
    });
}
function getClassSections(){
    let url = _URL['section_only_course'];
    let data = {
        'school_year': $('#school_year').val(),
        'year': $('#course_year').val()
    };
    $('#course_section').empty();
    $.get(url, data=data, function(data) {
        for(let sect of data){
            $('#course_section').append(`<option value="${sect.id}">${sect.section}</option>`);
        }

        $('#course_section').change()
    });
}

function getTeachers(){
    let url = _URL['hour_per_teacher_in_class'];
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val()
    };
    $.get(url, data=data, function(data) {
        $('#teachers_list').empty();
        for(let tea of data){
            let html = `
                <li class="list-group-item list-teachers">
                    <b>${tea.teacher.first_name} ${tea.teacher.last_name}</b> - ${tea.subject.name}<br/>
                    <div class="row font-italic">
                        <span class="col-9">${_TRANS['hours_teaching']}:</span>
                        <span class="col-3">${tea.hours}</span>
                    </div>
                    <div class="row font-italic">
                        <span class="col-9">${_TRANS['hours_bes']}</span>
                        <span class="col-3">${tea.hours_bes}</span>
                    </div>
                    <hr/>
                    <div class="row font-italic">
                        <span class="col-9">${_TRANS['missing_hours']}:</span>
                        <span class="col-3">${tea.missing_hours}</span>
                    </div>
                    <div class="row font-italic">
                        <span class="col-9">${_TRANS['hours_bes']}</span>
                        <span class="col-3">${tea.missing_hours_bes}</span>
                    </div>
                    <div class="row">
                        <button type="button" class="col-6 btn cal-event" onclick="teacherClick($(this).parent().parent(), ${tea.teacher.id}, ${tea.subject.id}, ${tea.school}, false)">${_TRANS['assign_lecture']}</button>
                        <button type="button" class="col-6 btn cal-event-bes" onclick="teacherClick($(this).parent().parent(), ${tea.teacher.id}, ${tea.subject.id}, ${tea.school}, true)">${_TRANS['assign_bes']}</button>
                    </div>
                </li>`;
            $('#teachers_list').append(html);
        }
    });
}

function getAssignments(startDate, endDate){
    let url = _URL['assignments'];
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    timetable.deleteAllEvents();
    $.get(url, data=data, function(data) {
        for(let assign of data){
            let blockId = assign.hour_slot;
            if(blockId === null){
                blockId = createExtraBlock(assign.date, assign.hour_start, assign.hour_end).id;
            }

            let teacher = assign.teacher.first_name + " " + assign.teacher.last_name;
            let customEvent = new Event(assign.id, teacher, assign.subject.name);
            let clickEvent = (event) => {
                alert("Lecture " + event.lecture + ", teacher " + event.teacher);
            };
            timetable.addEvent(customEvent, blockId, clickEvent, deleteAssignment);

            if(assign.bes){
                customEvent.htmlElement.addClass('cal-event-bes');
            }
            else if(assign.absent){
                customEvent.htmlElement.addClass('cal-event-absent');
            }
            else if(assign.substitution){
                customEvent.htmlElement.addClass('cal-event-substitution');
            }

            customEvent.htmlElement.tooltip({
                title: `
                    <b>${teacher}</b><br/>
                    ${assign.subject.name}<br/>
                    ${assign.hour_start.slice(0, -3)} - ${assign.hour_end.slice(0, -3)}
                `,
                html: true,
                boundary: 'window' 
            })
        }
    });
}

function getTeacherAssignments(startDate, endDate){
    let url = _URL['teacher_timetable'];
    let data = {
        'school_year': $('#school_year').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    timetable.deleteAllEvents();
    $.get(url, data=data, function(data) {
        for(let assign of data){
            let blockId = assign.hour_slot;
            if(blockId === null){
                blockId = createExtraBlock(assign.date, assign.hour_start, assign.hour_end).id;
            }

            let teacher = assign.teacher.first_name + " " + assign.teacher.last_name;
            let customEvent = new Event(assign.id, teacher, assign.subject.name);
            let clickEvent = (event) => {
                alert("Lecture " + event.lecture + ", teacher " + event.teacher);
            };
            timetable.addEvent(customEvent, blockId, clickEvent, deleteAssignment);

            if(assign.bes){
                customEvent.htmlElement.addClass('cal-event-bes');
            }
            else if(assign.absent){
                customEvent.htmlElement.addClass('cal-event-absent');
            }
            else if(assign.substitution){
                customEvent.htmlElement.addClass('cal-event-substitution');
            }

            customEvent.htmlElement.tooltip({
                title: `
                    <b>${teacher}</b><br/>
                    ${assign.subject.name}<br/>
                    ${assign.hour_start.slice(0, -3)} - ${assign.hour_end.slice(0, -3)}
                `,
                html: true,
                boundary: 'window' 
            })
        }
    });
}

function getHolidays(startDate, endDate){
    let url = _URL['holiday'];
    let data = {
        'school_year': $('#school_year').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    $.get(url, data=data, function(data) {
        for(let day of data){
            let start = moment(day.start);
            let end = moment(day.end);
            while(start <= end) {
                timetable.lockDay(start.weekday() - 1, day.name);
                start.add(1, 'days');
            }
        }
    });
}
function getStages(startDate, endDate){
    let url = _URL['stage'].replace('999999', $('#course_section').val());
    let data = {
        'school_year': $('#school_year').val(),
        'course': $('#course_section').val(),
        'from_date': formatDate(startDate),
        'to_date': formatDate(endDate)
    };
    $.get(url, data=data, function(data) {
        for(let day of data){
            let start = moment(day.start);
            let end = moment(day.end);
            while(start <= end) {
                timetable.lockDay(start.weekday() - 1, day.name);
                start.add(1, 'days');
            }
        }
    });
}

function teacherClick(btn, teacherId, subjId, schoolId, bes){
    btn = $(btn);

    if(!btn.hasClass('active')){
        btn.addClass('active');

        for(let blk of Object.keys(timetable.blocks)){
            timetable.getBlock(blk).setState('available');
            timetable.getBlock(blk).setOnClick((blk) => addAssignment(teacherId, subjId, schoolId, blk, bes));
        }

        setLockedBlocksTeacher(teacherId);
        setLockedBlocksAbsenceTeacher(teacherId);
    }
    else{
        btn.removeClass('active');

        timetable.resetAllBlocksStates();
    }
}

function setLockedBlocksTeacher(teacherId){
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
    $.get(url, data=data, function(data) {
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
    });
}

function setLockedBlocksAbsenceTeacher(teacherId){
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
    $.get(url, data=data, function(data) {
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
    });
}

function addAssignment(teacherId, subjId, schoolId, block, bes){
    let url = _URL['assignments'];

    let date = moment(currentDate).add(block.day, 'days').format('YYYY-MM-DD');
    let data = {
        csrfmiddlewaretoken: Cookies.get('csrftoken'),
        teacher_id: teacherId,
        course: $('#course_section').val(),
        subject_id: subjId,
        school_year: $('#school_year').val(),
        school: schoolId,
        date: date,
        hour_start: block.startTime.hours + ':' + block.startTime.min,
        hour_end: block.endTime.hours + ':' + block.endTime.min,
        bes: bes,
        substitution: false,
        absent: false
    };
    $.post(url, data=data, function(data) {
        loadData();
    });
}

function deleteAssignment(assign){
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

function checkReplicationAssignment(assign, startDate, endDate, resultList){
    let url = _URL['replicate_assignment']
        .replace("12345", assign.id)
        .replace("0000-00-00", formatDate(startDate))
        .replace("9999-99-99", formatDate(endDate));
    $.get(url, function(data) {
        let listConflict = ``;
        for(let conflict of data){
            listConflict += `
                <li>
                    <b>${conflict.teacher.first_name} ${conflict.teacher.last_name}</b> - ${conflict.subject.name}
                    ${conflict.hour_start}-${conflict.hour_end}
                </li>`;
        }

        let date = moment(startDate).add(assign.block.day, 'days').toDate();
        date = formatDate(date);

        resultList.append(`
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <span href="#submenu${assign.id}" data-toggle="collapse" aria-expanded="false">
                    <b>${assign.teacher}</b> - ${assign.lecture} ${date}
                    ${formatStringTime(assign.block.startTime)}-${formatStringTime(assign.block.endTime)}
                </span>
                <span class="badge badge-danger badge-pill">${data.length}</span>
            </li>
            <li class="list-group-item d-flex justify-content-between align-items-center conflicts-content">
                <ul class="collapse" id="submenu${assign.id}">
                    ${listConflict}
                </ul>
            </li>
        `);
    });        
}
function checkReplicateWeek(){
    let startDate = moment($('#date_start').val(), "MM/DD/YYYY").toDate();
    let endDate = moment($('#date_end').val(), "MM/DD/YYYY").toDate();

    let resultBox = $("#replicateResult");
    resultBox.empty();
    resultBox.append(`
        <b>Result:</b>
        <ul class="list-group">
        </ul>
    `);

    let resultList = resultBox.find('ul');

    for (let block of Object.keys(timetable.blocks)){
        for(let event of timetable.getBlock(block).events){
            checkReplicationAssignment(event, startDate, endDate, resultList);
        }
    }
}

function replicateAssignment(assign, startDate, endDate){
    let url = _URL['multiple_assignment']
        .replace("12345", assign.id)
        .replace("0000-00-00", formatDate(startDate))
        .replace("9999-99-99", formatDate(endDate));
    let data = {
        csrfmiddlewaretoken: Cookies.get('csrftoken')
    }
    $.ajax({
        url: url,
        type: 'POST',
        data: data,
        statusCode: {
            201: function(xhr) {
                alert(_TRANS['week_replicated_msg']);
            },
            400: function(xhr) {
                let data = xhr.responseJSON;
                console.error(data);
                alert(_TRANS['conflict_dates_msg'] + " " + data[0].date);                    
            }
        }
    });
}
function replicateWeek(){
    let startDate = moment($('#date_start').val(), "MM/DD/YYYY").toDate();
    let endDate = moment($('#date_end').val(), "MM/DD/YYYY").toDate();

    for (let block of Object.keys(timetable.blocks)){
        for(let event of timetable.getBlock(block).events){
            replicateAssignment(event, startDate, endDate);
        }
    }
}