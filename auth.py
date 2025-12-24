from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import db, USERS_COLLECTION
import random
from utils import send_email
from datetime import datetime

# Temporary in-memory OTP store
otp_store = {}

auth_bp = Blueprint('auth', __name__)

# ------------------- REGISTER -------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        existing = db.collection(USERS_COLLECTION).where("email", "==", email).limit(1).stream()
        if any(existing):
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Add new user
        db.collection(USERS_COLLECTION).add({
            "name": name,
            "email": email,
            "password": password,
            "is_admin": email == "pranavk9699@gmail.com",  # Admin flag
            "created_at": datetime.utcnow()
        })
        flash('Registered successfully. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ------------------- LOGIN -------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = db.collection(USERS_COLLECTION).where("email", "==", email).where("password", "==", password).limit(1).stream()
        user_doc = next(users, None)
        if user_doc:
            user = user_doc.to_dict()
            session['user_id'] = user_doc.id
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = user.get('is_admin', False)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# ------------------- LOGOUT -------------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


# ------------------- UPDATE PROFILE -------------------
@auth_bp.route('/update-profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        flash('Login required.', 'warning')
        return redirect(url_for('auth.login'))

    user_ref = db.collection(USERS_COLLECTION).document(session['user_id'])

    if request.method == 'POST':
        new_name = request.form['name']
        user_ref.update({"name": new_name})
        session['user_name'] = new_name
        flash("Profile updated successfully.", "success")
        return redirect(url_for('auth.update_profile'))

    user = user_ref.get().to_dict()
    return render_template('update_profile.html', user=user)


# ------------------- CHANGE PASSWORD -------------------
@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        flash('Please login to change password.', 'warning')
        return redirect(url_for('auth.login'))

    user_ref = db.collection(USERS_COLLECTION).document(session['user_id'])
    user = user_ref.get().to_dict()

    if request.method == 'POST':
        current_pw = request.form['current_password']
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']

        if new_pw != confirm_pw:
            flash('New passwords do not match.', 'danger')
        elif current_pw != user['password']:
            flash('Current password is incorrect.', 'danger')
        else:
            user_ref.update({"password": new_pw})
            flash('Password updated successfully.', 'success')

        return redirect(url_for('auth.change_password'))

    return render_template('change_password.html')


# ------------------- FORGOT PASSWORD -------------------
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        users = db.collection(USERS_COLLECTION).where("email", "==", email).limit(1).stream()
        user_doc = next(users, None)
        if user_doc:
            otp = random.randint(100000, 999999)
            otp_store[email] = otp

            sent = send_email("E-Waste Portal - OTP for Password Reset", f"Your OTP is: {otp}", email)
            if sent:
                session['otp_email'] = email
                flash('OTP sent to your email.', 'info')
                return redirect(url_for('auth.verify_otp'))
            else:
                flash('OTP send failed, please try again.', 'danger')
        else:
            flash('Email not found.', 'danger')

    return render_template('forgot_password.html')


# ------------------- VERIFY OTP -------------------
@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = session.get('otp_email')
        user_otp = request.form['otp']
        if email in otp_store and str(otp_store[email]) == user_otp:
            flash("OTP verified. Set your new password.", 'success')
            return redirect(url_for('auth.reset_password'))
        else:
            flash("Invalid OTP.", 'danger')

    return render_template('verify_otp.html')


# ------------------- RESET PASSWORD -------------------
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('otp_email')
    if not email:
        flash("Session expired. Please try again.", 'warning')
        return redirect(url_for('auth.forgot_password'))

    users_ref = db.collection(USERS_COLLECTION)
    user_doc = next(users_ref.where("email", "==", email).limit(1).stream(), None)
    if not user_doc:
        flash("User not found.", "danger")
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']
        if new_pw != confirm_pw:
            flash("Passwords do not match.", 'danger')
        else:
            db.collection(USERS_COLLECTION).document(user_doc.id).update({"password": new_pw})
            flash("Password updated successfully. Please login.", "success")
            otp_store.pop(email, None)
            session.pop('otp_email', None)
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html')
