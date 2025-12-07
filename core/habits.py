from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for, jsonify, current_app
)

from .helpers import login_required
from core.db import get_db

habits_bp = Blueprint('habits', __name__, url_prefix="/habits")

@habits_bp.route("/", methods=["GET", "POST"])
@login_required
def habits():
    context = {}
    db = get_db()
    user_id = session['user_id']
    if request.method == "POST":
        try:
            tracker_name = request.form.get('tracker-name')
            data_type = request.form.get('data-type')
            unit = request.form.get('unit')
            enum_options = request.form.get('enum-options')
            is_active = request.form.get('is-active') == 'on'
            db.execute("INSERT INTO custom_trackers (user_id, name, data_type, unit, enum_options, is_active) VALUES(?, ?, ?, ?, ?, ?)", (user_id, tracker_name, data_type, unit, enum_options, is_active))
            db.commit()
            flash(f"Tracker created successfully", "message")
        except Exception as error:
            flash(f"couldn't Create tracker: {error}", "error")
    trackers = db.execute("SELECT * FROM custom_trackers WHERE user_id=?", (user_id,)).fetchall()
    context["trackers"] = trackers
    return render_template("habits/habits-management.html", context=context)

@habits_bp.route("/<int:tracker_id>", methods=["POST", "DELETE"])
@login_required
def update_habit(tracker_id: int):
    user_id = session["user_id"]
    db = get_db()
    try:
        tracker = db.execute("SELECT * FROM custom_trackers WHERE user_id=? AND id=?", (user_id, tracker_id)).fetchone()
        if not tracker:
            flash(f"Could not find tracker with id: {tracker_id}", "error")
            return redirect(url_for('habits.habits'))
        tracker_name = request.form.get('tracker-name')
        data_type = request.form.get('data-type')
        unit = request.form.get('unit')
        enum_options = request.form.get('enum-options')
        is_active = request.form.get('is-active') == 'on'
        db.execute("UPDATE custom_trackers SET name=?, data_type=?, unit=?, enum_options=?, is_active=? WHERE user_id=? AND id=?", (tracker_name, data_type, unit, enum_options, is_active, user_id, tracker_id))
        db.commit()
        flash(f"Updated tracker successfully", "success")
    except Exception as error:
        flash(f"Could not update tracker with id: {tracker_id}: {error}", "error")
    return redirect(url_for('habits.habits'))

@habits_bp.route("/<int:tracker_id>/delete")
@login_required
def delete_habit(tracker_id: int):
    user_id = session["user_id"]
    db = get_db()
    try:
        tracker = db.execute("SELECT * FROM custom_trackers WHERE user_id=? AND id=?", (user_id, tracker_id)).fetchone()
        if not tracker:
            flash(f"Could not find tracker with id: {tracker_id}", "error")
            return redirect(url_for('habits.habits'))
        db.execute("DELETE FROM  custom_trackers WHERE user_id=? AND id=?", (user_id, tracker_id))
        db.commit()
        flash(f"Deleted tracker successfully", "success")
    except Exception as error:
        flash(f"Could not delete tracker with id: {tracker_id}", "error")
    return redirect(url_for('habits.habits'))

