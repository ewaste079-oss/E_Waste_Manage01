from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, send_file
from db import db, USERS_COLLECTION, EWASTE_COLLECTION
import io
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -------------------- DASHBOARD --------------------
@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Access denied. Admins only.', 'danger')
        return redirect(url_for('index'))

    # Fetch all users
    users = [doc.to_dict() | {"id": doc.id} for doc in db.collection(USERS_COLLECTION).stream()]

    # Fetch all e-waste entries
    waste = [doc.to_dict() | {"id": doc.id} for doc in db.collection(EWASTE_COLLECTION).stream()]

    admin_user = next((u for u in users if u.get("is_admin")), None)
    admin_name = admin_user['name'] if admin_user else "Admin"
    admin_email = admin_user['email'] if admin_user else "admin@example.com"

    return render_template('admin.html',
                           users=users,
                           waste=waste,
                           admin_name=admin_name,
                           admin_email=admin_email)


# -------------------- DELETE USER --------------------
@admin_bp.route('/delete_user/<id>')  # <-- int काढलं
def delete_user(id):
    db.collection(USERS_COLLECTION).document(id).delete()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.dashboard'))

# -------------------- REPORT USER --------------------
@admin_bp.route('/report_user/<id>')  # <-- int काढलं
def report_user(id):
    user_doc = db.collection(USERS_COLLECTION).document(id).get()
    if user_doc.exists:
        flash(f"User '{user_doc.to_dict().get('name')}' has been reported for misbehavior.", "warning")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('admin.dashboard'))

# -------------------- DELETE E-WASTE --------------------
@admin_bp.route('/delete_waste/<id>')  # <-- int काढलं
def delete_waste(id):
    db.collection(EWASTE_COLLECTION).document(id).delete()
    flash('E-Waste record deleted.', 'success')
    return redirect(url_for('admin.dashboard'))


# -------------------- DOWNLOAD EXCEL --------------------
@admin_bp.route('/download_excel')
def download_excel():
    waste = [doc.to_dict() for doc in db.collection(EWASTE_COLLECTION).stream()]
    df = pd.DataFrame(waste)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='E-Waste')
    output.seek(0)
    return send_file(output,
                     download_name='e-waste-report.xlsx',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


# -------------------- DOWNLOAD CSV --------------------
@admin_bp.route('/download_csv')
def download_csv():
    waste = [doc.to_dict() for doc in db.collection(EWASTE_COLLECTION).stream()]
    df = pd.DataFrame(waste)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=e-waste-report.csv"
    response.headers["Content-type"] = "text/csv"
    return response
