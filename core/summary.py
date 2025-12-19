import ast
from collections import defaultdict
from datetime import datetime
from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for, jsonify, current_app
)
from .utils import time_to_minutes, get_month_name

from .helpers import login_required
from core.db import get_db

summary_bp = Blueprint('summary', __name__, url_prefix="/summary")

@summary_bp.route("/", methods=['GET'])
@login_required
def get_summary():
    user_id = session['user_id']
    if request.args.get('date'):
        month = request.args.get('date')[5:]
        year = request.args.get('date')[:4]
    else:
        month = datetime.now().month
        year = datetime.now().year
    try:
        month = int(month)
        year = int(year)
        if month > 12 or month < 1:
            raise ValueError('Not valid month')
    except:
        month = datetime.now().month
        year = datetime.now().year

    db = get_db()
    diary_entries = db.execute("SELECT * FROM diary_entry WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    personal_trackers_data = db.execute("SELECT date, wakeup_time, sleep_time, screen_time, water_intake, exercise, outgoing, mood FROM personal_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    work_trackers_data = db.execute("SELECT date, commute_time, return_time, break_time, given_work, completed_work, is_off FROM work_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    custom_trackers_data = db.execute("SELECT * FROM custom_trackers_data WHERE strftime('%Y-%m', date) = ? AND user_id=?", (f'{year}-{month}', user_id)).fetchall()
    personal_trackers_data_compute = defaultdict(list)
    for idx, key in enumerate(["date", "wakeup_time", "sleep_time", "screen_time", "water_intake", "exercise", "outgoing", "mood"]):
        for row in personal_trackers_data:
            if key == "date":
                personal_trackers_data_compute[key].append(row[idx].isoformat())
            elif "time" in key:
                personal_trackers_data_compute[key].append(time_to_minutes(row[idx]))
            else:
                personal_trackers_data_compute[key].append(row[idx])
    
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