from collections import defaultdict, Counter
from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for, jsonify, current_app
)
from .utils import time_to_minutes, get_month_name, get_month_year, min_to_hrs, sample_variance

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
        if val:
            avg_mood += int(val)
            count += 1
        if val in mood_distribution:
            mood_distribution[val] += 1
        else:
            mood_distribution[val] = 1
    if count > 0:
        avg_mood /= count

    # water Intake
    avg_water_intake = 0
    count = 0
    water_distribution = {}
    for val, _ in water_intakes:
        if val:
            avg_water_intake += float(val)
            count += 1
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
    exercise_distribution = {0:0, 1:0, 2:0, 3:0}
    count = 0
    for val, date in exercise_data:
        if val is not None:
            avg_exercise += int(val)
            count += 1
        if val in exercise_distribution:
            exercise_distribution[val] += 1
        else:
            exercise_distribution[val] = 1
        exercise_streak = max(curr_streak, exercise_streak)
    if count:
        avg_exercise /= count
    
    # avg_outgoing = 0
    # outgoing_streak = 0
    # curr_streak = 0
    # outgoing_distribution = 0
    # count = 0
    # for val, date in outgoing_data:
    #     if val is not None:
    #         avg_outgoing += int(val)
    #         count += 1
    #     if val in outgoing_distribution:
    #         outgoing_distribution[val] += 1
    #     else:
    #         outgoing_distribution[val] = 1
    #     outgoing_streak = max(curr_streak, outgoing_streak)

    # avg_outgoing /= count




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
            "data": exercise_data
        },
    #     "outgoing":{
    #         "avg": avg_outgoing,
    #         "distribution": outgoing_distribution,
    #         "streak": outgoing_streak,
    #         "data": outgoing_data
    #     },
    }
    # - no diary data
    # - avg mood rating -> count of No entry, and entry of each type of mood count
    # - avg water rating , how many times water is greater than 2.5 litera set limits 
    # - screen time data with none value tackled, avg time, min time, max time
    # - sleep duration calculated, none value tackeld, average wake up and sleep time, variance of sleep durations 
    # - exercise count of each type of exercise average score and streak of medium to heavy exercise 
    # - outgoing count of each type of outgoing average score and streak of medium to heavy outgoing
    return data

@summary_bp.route("/", methods=['GET'])
@login_required
def get_summary():
    user_id = session['user_id']
    month, year =  get_month_year(request.args.get('date'))
    month_days = monthrange(year, month)
    db = get_db()

    user_journal_days = [day['day'] for day in db.execute("SELECT CAST(strftime('%d', date) AS INTEGER) AS day FROM diary_entry WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id) ).fetchall()]
    diary_entries = db.execute("SELECT * FROM diary_entry WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    personal_trackers_data = db.execute("SELECT CAST(strftime('%d', date) AS INTEGER) AS day_date,* FROM personal_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    personal_trackers_data_compute = prepare_personal_trackers_date(personal_trackers_data)
    work_trackers_data = db.execute("SELECT date, commute_time, return_time, break_time, given_work, completed_work, is_off FROM work_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    custom_trackers_data = db.execute("SELECT * FROM custom_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    # personal_trackers_data_compute = defaultdict(list)
    # for idx, key in enumerate(["date", "wakeup_time", "sleep_time", "screen_time", "water_intake", "exercise", "outgoing", "mood"]):
    #     for row in personal_trackers_data:
    #         if key == "date":
    #             personal_trackers_data_compute[key].append(row[idx].isoformat())
    #         elif "time" in key:
    #             personal_trackers_data_compute[key].append(time_to_minutes(row[idx]))
    #         else:
    #             personal_trackers_data_compute[key].append(row[idx])
    
    work_trackers_data_compute = {}
    off_days = 0
    total_days = 0
    for idx, key in enumerate(["date", "commute_time", "return_time", "break_time", "given_work", "completed_work", "is_off"]):
        work_trackers_data_compute[key] = []
        for row in work_trackers_data:
            if key == "date":
                work_trackers_data_compute[key].append(row[idx].isoformat())
            elif "time" in key:
                work_trackers_data_compute[key].append(time_to_minutes(row[idx]))
            else:
                work_trackers_data_compute[key].append(row[idx])
            if row[-1] == True:
                off_days += 1
            total_days += 1

    work_trackers_data_compute['off_days'] = off_days
    work_trackers_data_compute['total_days'] = total_days

    print(personal_trackers_data_compute)
    context={
        'entries_day': user_journal_days,
        'diary_entries': diary_entries,
        'personal_trackers_data': personal_trackers_data,
        'personal_trackers_data_compute': personal_trackers_data_compute,
        'work_trackers_data_compute': work_trackers_data_compute,
        'work_trackers_data': work_trackers_data,
        'custom_trackers_data': custom_trackers_data,
        'month': {"month_num": month, "month_name": get_month_name(month)},
        'year': year
    }

    return render_template('summary/summary_diary.html', context=context)


# data to be send
# - total days of month, array of entry days 
# - no diary data
# - avg mood rating -> count of No entry, and entry of each type of mood count
# - avg water rating , how many times water is greater than 2.5 litera set limits 
# - screen time data with none value tackled, avg time, min time, max time
# - sleep duration calculated, none value tackeld, average wake up and sleep time, variance of sleep durations 
# - exercise count of each type of exercise average score and streak of medium to heavy exercise 
# - outgoing count of each type of outgoing average score and streak of medium to heavy outgoing

# -- work related 
# = office time same as sleep data
# - count of off days work total leaves and holidays 
# - breaks same as sleep data 
# - work load aevrage and top two type of workload and how much they cover 

# -- data for workload calculation and productivity data 



# SELECT date, commute_time, return_time, break_time, given_work, completed_work, is_off FROM work_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?