import ast
from datetime import datetime
from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for, jsonify, current_app
)

from .helpers import login_required
from core.db import get_db

day_entry_bp = Blueprint('diary', __name__, url_prefix="/diary")

@day_entry_bp.route("/day", methods=["GET", "POST"])
@login_required
def user_day_entry():
    user_id = session['user_id']
    date = request.args.get('date', datetime.now().date())
    db = get_db()
    day_entry_for_user = db.execute("SELECT * FROM user_day WHERE date=? AND user_id=?", (date, user_id)).fetchone()
    if not day_entry_for_user:
        diary_id = db.execute("INSERT INTO diary_entry (user_id, date) VALUES(?, ?)", (user_id, date)).lastrowid
        personal_tracker_id = db.execute("INSERT INTO personal_trackers_data (user_id, date) VALUES(?, ?)", (user_id, date)).lastrowid
        work_tracker_id = db.execute("INSERT INTO work_trackers_data (user_id, date) VALUES(?, ?)", (user_id, date)).lastrowid
        db.execute("INSERT INTO user_day (user_id, date, diary_entry_id, personal_trackers_id, work_trackers_id) VALUES(?, ?, ?, ?, ?)", (user_id, date, diary_id, personal_tracker_id, work_tracker_id))
        db.commit()
        return redirect(url_for('diary.user_day_entry',  date=date))
    diary = db.execute("SELECT * FROM diary_entry WHERE id=?", (day_entry_for_user["diary_entry_id"],)).fetchone()
    personal_tracker = db.execute("SELECT * FROM personal_trackers_data WHERE id=?", (day_entry_for_user["personal_trackers_id"],)).fetchone()
    work_tracker = db.execute("SELECT * FROM work_trackers_data WHERE id=?", (day_entry_for_user["work_trackers_id"],)).fetchone()
    
    # custom trackers
    custom_tracker_raw_ids = day_entry_for_user["custom_tracker_data_list_ids"]
    ids = ast.literal_eval(custom_tracker_raw_ids) if custom_tracker_raw_ids else []
    sql = """
        SELECT 
            ct.id                AS tracker_id,
            ct.name              AS name,
            ct.data_type         AS data_type,
            ct.enum_options      AS enum_options,
            ctd.value            AS value,
            ctd.date             AS date
        FROM custom_trackers ct
        LEFT JOIN custom_trackers_data ctd
            ON ct.id = ctd.tracker_id
            AND ctd.user_id = ?
            AND ctd.date = ?
        WHERE ct.user_id = ?
        AND ct.is_active = 1
        ORDER BY ct.id ASC
    """
    custom_trackers = [] # db.execute(sql, (user_id, date, user_id)).fetchall()
    
    context = {
        "day_entry_for_user": day_entry_for_user,
        "diary": diary,
        "personal_tracker": personal_tracker,
        "work_tracker": work_tracker,
        "custom_trackers": custom_trackers
    }

    if request.method == "POST":
        data = request.form
        try:
            date = data.get('entry-date')
            # diary
            short_note = data.get('short-note')
            long_entry = data.get('long-entry')
            # personal
            wakeUp_time = data.get('wake-up-time')
            sleep_time = data.get('sleep-time')
            screen_time = data.get('screen-time')
            water_intake = data.get('water-intake')
            exercise = data.get('exercise')
            outgoing = data.get('outgoing')
            mood = data.get('mood')
            # work
            commute_time = data.get('commute-time')
            return_time = data.get('return-time')
            break_time = data.get('break-time')
            given_work = data.get('given-work')
            completed_work = data.get('completed-work')
            workload = data.get('workload')
            is_off  = data.get('off-day') == "on"

            for tracker in custom_trackers:
                field_name = f"custom-tracker-{tracker['name']}-{tracker['tracker_id']}"
                value = request.form.get(field_name)
                if tracker['data_type'] == "boolean":
                    value = (value=='on')

                if value is not None:
                    existing = db.execute("""
                        SELECT id FROM custom_trackers_data
                        WHERE user_id = ? AND tracker_id = ? AND date = ?
                    """, (user_id, tracker["tracker_id"], date)).fetchone()

                    if existing:
                        db.execute("""
                            UPDATE custom_trackers_data
                            SET value = ?
                            WHERE id = ?
                        """, (value, existing["id"]))
                    else:
                        db.execute("""
                            INSERT INTO custom_trackers_data (user_id, tracker_id, date, value)
                            VALUES (?, ?, ?, ?)
                        """, (user_id, tracker["tracker_id"], date, value))
                
                # NOTE: Need to try this query 
                # db.execute("""
                #     INSERT INTO custom_trackers_data (user_id, tracker_id, date, value)
                #     VALUES (?, ?, ?, ?)
                #     ON CONFLICT(user_id, tracker_id, date)
                #     DO UPDATE SET value = excluded.value
                # """, (user_id, tracker["id"], date, value))


            db.execute("UPDATE diary_entry \
                    SET short_note=?, long_entry=? \
                    WHERE user_id=? AND date=?", (short_note, long_entry, user_id, date))
            db.execute("UPDATE personal_trackers_data \
                    SET wakeup_time=?, sleep_time=?, screen_time=?, water_intake=?, exercise=?, outgoing=?, mood=?\
                    WHERE user_id=? AND date=?", (wakeUp_time, sleep_time, screen_time, water_intake, exercise, outgoing, mood, user_id, date))
            db.execute("UPDATE work_trackers_data \
                    SET commute_time=?, return_time=?, break_time=?, given_work=?, completed_work=?, workload=?, is_off=?\
                    WHERE user_id=? AND date=?", (commute_time, return_time, break_time, given_work, completed_work, workload, is_off, user_id, date))
            db.commit()
            flash("Updated successfully", "success")
            return redirect(url_for('diary.user_day_entry',  date=date))
        except Exception as error:
            flash(f"Couldn't update entry: {error}", "error")
    
    return render_template("day_entry/day_entry.html", context=context)

