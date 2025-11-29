import functools
from flask import (
    Blueprint, redirect, render_template, request, session, flash, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .helpers import login_required
from .auth_utils import validate_email, validate_username
from core.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        error = None
        try:
            if request.form.get('password') != request.form.get('confirmation'):
                raise ValueError("Password doesn't match")
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            firstname = request.form.get("firstname", username)
            lastname = request.form.get("lastname", "")

            if not validate_email(email):
                raise ValueError("Email is not correct format")
            if not validate_username(username):
                raise ValueError("Username can only contain alphanumeric and underscore and must be of length 4 to 32")
            
            db = get_db()
            try:
                user_id = db.execute("INSERT INTO accounts (username, email, password) VALUES(?, ?, ?)", (username, email, generate_password_hash(password))).lastrowid
                db.execute("INSERT INTO user_profiles (user_id, first_name, last_name) VALUES(?, ?, ?)", (user_id, firstname, lastname))
                db.commit()
                session["user_id"] = user_id
            except db.IntegrityError:
                raise Exception("This username or email already exist.")
            except:
                raise Exception("Invalid data.")
            flash("Signed Up successfully", "info")
            return redirect("/auth/profile")
        except Exception as err:
            error = err
            flash(error, "error")

    return render_template("auth/register_user.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login_user():
    session.clear()
    if request.method == "POST":
        username_email = request.form.get("user_identifier")
        password = request.form.get("password")
        if not (validate_username(username_email) or validate_email(username_email)):
            raise ValueError("Not valid username or email")
        db = get_db()
        try:
            user = db.execute("SELECT * FROM accounts WHERE username = ? OR email = ?", (username_email, username_email)).fetchone()
            if not user:
                raise ValueError("User with this email or username not found")
            if not check_password_hash(user["password"], password):
                raise ValueError("Incorrect password")
             # Remember which user has logged in
            session["user_id"] = user["id"]
            flash("Logged In", "info")
        except Exception as error:
            flash(error, "error")
    return render_template("auth/login_user.html")


@auth_bp.route("/logout", methods=["POST", "GET"])
@login_required
def logout_user():
    session.clear()
    return redirect("/")

@auth_bp.route("/profile", methods=["GET", "POST", "PUT"])
@login_required
def profile_user():
    user_id = session.get("user_id")
    db = get_db()
    user_profile = db.execute(
        "SELECT acc.id, acc.username, acc.email, acc.created_at AS account_created, acc.modified_at AS account_update, \
        pr.first_name, pr.last_name, pr.profile_pic, pr.date_of_birth, pr.created_at AS profile_created, pr.modified_at profile_updated, \
        loc.city, loc.country \
        FROM accounts AS acc \
        JOIN user_profiles AS pr \
        ON acc.id = pr.user_id  \
        LEFT JOIN locations as loc \
        ON loc.id = pr.location_id \
        WHERE acc.id = ?", (user_id, )).fetchone()
    
    return render_template("auth/profile_user.html", user_profile=user_profile)