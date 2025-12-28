from collections import defaultdict, Counter
from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for, jsonify, current_app
)
from .utils import time_to_minutes, get_month_name, get_month_year, min_to_hrs, sample_variance, get_month_days, min_to_time, min_to_human_time

from .helpers import login_required
from core.db import get_db
from calendar import monthrange

summary_bp = Blueprint('summary', __name__, url_prefix="/summary")

def prepare_personal_trackers_date(raw_data):
    # data to be send
    # - total days of month, array of entry days
    mood_emojis = {0: '⚪', 1:'😞', 2:'😕', 3:'😐', 4:'🙂', 5:'😄'}
    days = []
    water_intakes = []
    sleep_time = []
    screen_time = []
    exercise_data = []
    outgoing_data = []
    mood_data = []
    for row in raw_data:
        days.append(row['day_date'])
        water_intakes.append([row['water_intake'], row['day_date']])
        sleep_time.append([[row['wakeup_time'], row['sleep_time']], row['day_date']])
        screen_time.append([time_to_minutes(row['screen_time']), row['day_date']])
        exercise_data.append([row['exercise'], row['day_date']]) 
        outgoing_data.append([row['outgoing'], row['day_date']])
        mood_data.append([row['mood'], row['day_date']])

    # mood
    avg_mood = 0
    count = 0
    mood_distribution = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
    for val, _ in mood_data:
        try:
            val = int(val)
            avg_mood += val
            count += 1
        except:
            val = 0
        mood_distribution[val] += 1

    if count > 0:
        avg_mood /= count

    # water Intake
    avg_water_intake = 0
    count = 0
    water_distribution = {}
    for val, _ in water_intakes:
        try:
            val = float(val)
            avg_water_intake += val
            count += 1
        except:
            val = 0
        if val in water_distribution:
            water_distribution[val] += 1
        else:
            water_distribution[val] = 1
    if count > 0:
        avg_water_intake /= count
    goal_achieved_days = sum([float(val) > 2.4 for val, _ in water_intakes if val])

    # sleep cycle 
    avg_sleep_duration = 0
    sleep_durations = []
    avg_wakeup_time = 0
    avg_sleep_time = 0
    sleep_consistency = 0 # variance of sleep duration
    count = 0
    for val, date in sleep_time:
        wakeup, sleep = val
        wakeup, sleep = time_to_minutes(wakeup), time_to_minutes(sleep)
        duration = abs((time_to_minutes('24:00')-sleep)+wakeup)
        sleep_durations.append([duration, date])
        avg_sleep_duration += duration
        count += 1
        avg_wakeup_time += wakeup
        avg_sleep_time += sleep
    if count:
        avg_wakeup_time /= count
        avg_sleep_duration /= count
        avg_sleep_time /= count
    
    sleep_consistency = min_to_hrs(sample_variance([val for val, _ in sleep_durations]))

    # screen time
    avg_screen_time = 0
    count = 0
    for val, _ in screen_time:
        if val is not None:
            avg_screen_time += val
            count += 1
    if count > 0:
        avg_screen_time /= count

    # exercise 
    avg_exercise = 0
    exercise_streak = 0
    curr_streak = 0
    exercise_distribution = {0:0, 1:0, 2:0, 3:0, }
    count = 0
    prev_date = -1
    for val, date in exercise_data:
        try:
            val = int(val)
            avg_exercise +=  val
            count += 1
        except:
            avg_exercise += 0
            val = 0
        if val and prev_date == date-1:
            curr_streak += 1
        else:
            curr_streak = 1
        prev_date = date
        exercise_distribution[val] += 1
        exercise_streak = max(curr_streak, exercise_streak)

    if count:
        avg_exercise /= count
    
    total_outgoing_days = 0
    most_common = 0
    outgoing_streak = 0
    curr_streak = 0
    outgoing_distribution = {0:0, 1:0, 2:0, 3:0}
    count = 0
    prev_date = -1
    for val, date in outgoing_data:
        try:
            val = int(val)
            if val:
                total_outgoing_days +=  1
            count += 1
        except:
            val = 0
        if val and prev_date == date-1:
            curr_streak += 1
        else:
            curr_streak = 1
        prev_date = date
        outgoing_distribution[val] += 1
        outgoing_streak = max(curr_streak, outgoing_streak)
    
    most_common = sorted(outgoing_distribution.items(), key=lambda item: item[1], reverse=True)[1][0]


    data = {
        "days":days,
        "mood": {
            "avg": {"val": avg_mood, "emoji": mood_emojis[round(avg_mood)%5]},
            "distribution": mood_distribution,
            "moods": mood_data 
        },
        "water":{
            "avg": avg_water_intake,
            "data": water_intakes,
            "distribution": water_distribution,
            "goal_achieved_days": round((goal_achieved_days*100)/len(days)) if days else 0
        },
        "sleep":{
            "avg_duration": min_to_hrs(avg_sleep_duration),
            "avg_wakeup_time": avg_wakeup_time,
            "avg_sleep_time": avg_sleep_time,
            "variance": sleep_consistency,
            "variance_human": min_to_human_time(sleep_consistency),
            "sleep_duration_data": sleep_durations,
            "data": sleep_time
        },
        "screen_time":{
            "avg": min_to_hrs(avg_screen_time),
            "data": screen_time
        },
        "exercise":{
            "avg": avg_exercise,
            "distribution": exercise_distribution,
            "streak": exercise_streak,
            "data": exercise_data,
            "days": sum(exercise_distribution.values())-exercise_distribution[0]
        },
        "outgoing":{
            "total_days": total_outgoing_days,
            "most_common": most_common,
            "distribution": outgoing_distribution,
            "streak": outgoing_streak,
            "data": outgoing_data
        },
    }
    return data

def prepare_work_trackers_date(raw_data):
    # data to be send
    # - total days of month, array of entry days
    workload_dict = {0:'none', 1:'Ehh', 2:'ok', 3:'usual', 4:'tiring', 5:'hectic'}
    days = []
    office_time_data = []
    break_time_data = []
    workload_data = []
    assignments_data = []

    work_off_days = 0
    work_holidays = 0
    work_leave_days = 0
    work_work_days = 0

    for row in raw_data:
        days.append(row['day_date'])
        if not row['is_off']:
            office_time_data.append([[row['commute_time'], row['return_time']], row['day_date']])
            break_time_data.append([time_to_minutes(row['break_time']), row['day_date']])
            workload_data.append([int(row['workload'] or 0), row['day_date']])
            assignments_data.append([[int(row['completed_work'] or 0), int(row['given_work'] or 0)], row['day_date']])
            work_work_days += 1
        else:
            assignments_data.append([[0, 0], row['day_date']])
            work_off_days += 1
            work_holidays += 1
            work_leave_days += 1
    
    # workload
    avg_workload = 0
    count = 0
    workload_distribution = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0}
    for val, _ in workload_data:
        avg_workload += val
        count += 1
        workload_distribution[val] += 1
    
    top_two_workload = [[workload_dict[i[0]], i[1]] for i in sorted(list(workload_distribution.items())[1:], key=lambda item: item[1], reverse=True)[:2]]
    if work_work_days:
        top_two_workload_percentage = (sum([i[1] for i in top_two_workload])/work_work_days)*100
    else:
        top_two_workload_percentage = 0

    if count > 0:
        avg_workload /= count

    # office time  cycle 
    avg_office_duration = 0
    office_durations = []
    avg_commute_time = 0
    avg_return_time = 0
    time_consistency = 0 # variance of sleep duration
    office_change_in_duration = 0
    count = 0
    for val, date in office_time_data:
        commute, return_time = val
        commute, return_time = time_to_minutes(commute), time_to_minutes(return_time)
        duration = (return_time - commute) if return_time >= commute else (1440 - commute + return_time)
        office_durations.append([duration, date])
        avg_office_duration += duration
        count += 1
        avg_commute_time += commute
        avg_return_time += return_time
    if count:
        avg_commute_time /= count
        avg_office_duration /= count
        avg_return_time /= count
    
    time_consistency = min_to_hrs(sample_variance([val for val, _ in office_durations]))

    # break time
    avg_break_time = 0
    min_break_time = 24*60
    max_break_time = 0
    count = 0
    no_break_days = 0
    for val, _ in break_time_data:
        if val is not None and val==0:
            no_break_days += 1
        try:
            val = int(val)
            if val:
                avg_break_time += val
                min_break_time = min(min_break_time, val)
                max_break_time = max(max_break_time, val)
            count += 1
        except:
            val = 0
        
    if count > 0:
        avg_break_time /= count

    # assignments
    total_assigned_work = 0
    completed_assigned_work = 0
    completion_percentage_work = 100
    pending_work_days = 0
    backlog_completion_days = 0
    perfect_work_days = 0
    productivity_score = 0
    for (comp, assign), _ in assignments_data:
        if (comp == 0 and assign==0):
            continue
        total_assigned_work += assign 
        completed_assigned_work += comp
        if comp > assign:
            backlog_completion_days+= 1
        elif assign > comp:
            pending_work_days += 1
        else:
            perfect_work_days += 1
    if total_assigned_work:
        completion_percentage_work = (completed_assigned_work/total_assigned_work)*100
    if work_work_days:
        productivity_score = (completion_percentage_work * 0.6) + ((perfect_work_days / work_work_days) * 100 * 0.25) - ((pending_work_days / work_work_days) * 100 * 0.15)

    # time_consistency is already variance in minutes
    if time_consistency <= 30:
        punctuality_score = 100
    elif time_consistency >= 120:
        punctuality_score = 40
    else:
        punctuality_score = round(100 - ((time_consistency - 30) / 90) * 60)
    
    if time_consistency <= 45:
        consistency_score = 100
    elif time_consistency >= 180:
        consistency_score = 30
    else:
        consistency_score = round(100 - ((time_consistency - 45) / 135) * 70)
    
    heavy_days = workload_distribution[4] + workload_distribution[5]
    light_days = workload_distribution[0] + workload_distribution[1]

    if work_work_days:
        overload_ratio = heavy_days / work_work_days
        underload_ratio = light_days / work_work_days

        workload_score = round(
            100
            - overload_ratio * 50
            - underload_ratio * 30
        )
    else:
        workload_score = 0

    workload_score = max(0, min(100, workload_score))

    if work_work_days:
        no_break_penalty = (no_break_days / work_work_days) * 40

        if avg_break_time < 30:
            break_score = 60
        elif avg_break_time <= 90:
            break_score = 100
        else:
            break_score = 70

        break_score -= no_break_penalty
    else:
        break_score = 0

    break_score = max(0, round(break_score))





    data = {
        "days":days,
        "workload": {
            "avg": {"val": avg_workload, "word": workload_dict[round(avg_workload)%5]},
            "distribution": workload_distribution,
            "moods": workload_data,
            "top_two_workload": top_two_workload, 
            "top_two_workload_percentage": top_two_workload_percentage,
        },
        "office_time":{
            "avg_duration": min_to_hrs(avg_office_duration),
            "change_in_duration": min_to_hrs(office_change_in_duration),
            "avg_commute_time": min_to_time(avg_commute_time),
            "avg_return_time": min_to_time(avg_return_time),
            "variance": time_consistency,
            "variance_human": min_to_human_time(time_consistency),
            "office_duration_data": office_durations,
            "data": office_time_data
        },
        "break_time":{
            "avg": avg_break_time,
            "max_break_time": max_break_time,
            "min_break_time": min_break_time,
            "no_break_days": no_break_days,
            "data": break_time_data
        },
        "work_off_days":work_off_days,
        "work_holidays":work_holidays,
        "work_leave_days":work_leave_days,
        "work_work_days":work_work_days,
        "assignments":{
            "data": assignments_data,
            "total_assigned_work": total_assigned_work,
            "completed_assigned_work": completed_assigned_work,
            "percentage_work": completion_percentage_work,
            "pending_work_days": pending_work_days,
            "backlog_completion_days": backlog_completion_days,
            "perfect_work_days": perfect_work_days,
        },
        "radar_data":{
            "productivity_score": productivity_score,
            "punctuality_score": punctuality_score,
            "consistency_score": consistency_score,
            "workload_score": workload_score,
            "break_score": break_score,
        }
    }
    return data

@summary_bp.route("/", methods=['GET'])
@login_required
def get_summary():
    user_id = session['user_id']
    month, year =  get_month_year(request.args.get('date'))
    db = get_db()

    user_journal_days = [day['day'] for day in db.execute("SELECT CAST(strftime('%d', date) AS INTEGER) AS day FROM diary_entry WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id) ).fetchall()]
    diary_entries = db.execute("SELECT * FROM diary_entry WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    personal_trackers_data = db.execute("SELECT CAST(strftime('%d', date) AS INTEGER) AS day_date,* FROM personal_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    personal_trackers_data_compute = prepare_personal_trackers_date(personal_trackers_data)
    work_trackers_data = db.execute("SELECT CAST(strftime('%d', date) AS INTEGER) AS day_date,* FROM work_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    work_trackers_data_compute = prepare_work_trackers_date(work_trackers_data)
    custom_trackers_data = db.execute("SELECT * FROM custom_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()

    context={
        'entries_day': user_journal_days,
        'diary_entries': diary_entries,
        'personal_trackers_data': personal_trackers_data,
        'personal_trackers_data_compute': personal_trackers_data_compute,
        'work_trackers_data_compute': work_trackers_data_compute,
        'work_trackers_data': work_trackers_data,
        'custom_trackers_data': custom_trackers_data,
        'month': {"month_num": month, "month_name": get_month_name(month), "month_days": get_month_days(month)},
        'year': year
    }

    return render_template('summary/summary_diary.html', context=context)