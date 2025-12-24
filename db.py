import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta, timezone

# -------------------- Firebase Initialization --------------------
cred = credentials.Certificate(
    r"C:\Users\HP\OneDrive\Attachments\Desktop\E_WASTE\data\e-waste-c032c-firebase-adminsdk-fbsvc-48bb16b1ba.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------- Collections --------------------
USERS_COLLECTION = "users"
EWASTE_COLLECTION = "ewaste"
MESSAGES_COLLECTION = "messages"
REPORTS_COLLECTION = "reports"

# -------------------- Users --------------------
def insert_admin_user(name, email, password):
    """Insert an admin user if not exists."""
    users_ref = db.collection(USERS_COLLECTION)
    query = users_ref.where("email", "==", email).limit(1).stream()
    if any(query):
        print("⚠️ Admin already exists or email is duplicate.")
        return
    users_ref.document().set({
        "name": name,
        "email": email,
        "password": password,
        "is_admin": True,
        "created_at": datetime
    })
    print(f"✅ Admin user {email} added.")

def get_admin_user():
    """Return first admin user as dict."""
    users_ref = db.collection(USERS_COLLECTION)
    admins = users_ref.where("is_admin", "==", True).limit(1).stream()
    for admin in admins:
        data = admin.to_dict()
        data["id"] = admin.id
        return data
    return None

def get_user_by_email(email):
    """Return user dict by email."""
    users_ref = db.collection(USERS_COLLECTION)
    users = users_ref.where("email", "==", email).limit(1).stream()
    for user in users:
        data = user.to_dict()
        data["id"] = user.id
        return data
    return None

def update_user(user_id, data: dict):
    """Update user fields by ID."""
    db.collection(USERS_COLLECTION).document(user_id).update(data)

def delete_user(user_id):
    db.collection(USERS_COLLECTION).document(user_id).delete()

# ---------------- E-Waste Entry ----------------
def insert_ewaste(user_id, item_name, category, condition, weight, location):
    """Add e-waste entry with UTC timestamp, auto-convert to IST if needed."""
    
    # Auto UTC timestamp
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    
    # Save to Firestore
    doc_ref = db.collection(EWASTE_COLLECTION).add({
        "user_id": user_id,
        "item_name": item_name,
        "category": category,
        "condition": condition,
        "weight": weight,
        "location": location,
        "date_utc": utc_now.isoformat()  # Store UTC
    })
    
    # Optional: Convert UTC to IST for printing/log
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_now + ist_offset
    
    print(f"✅ E-waste '{item_name}' added for user_id={user_id}")
    print(f"UTC Time: {utc_now}")
    print(f"IST Time: {ist_time}")

def delete_ewaste(waste_id):
    db.collection(EWASTE_COLLECTION).document(waste_id).delete()

# -------------------- Messages --------------------
def insert_message(name, email, message):
    db.collection(MESSAGES_COLLECTION).add({
        "name": name,
        "email": email,
        "message": message,
        "created_at": datetime
    })
    print(f"✅ Message from {name} added.")

# -------------------- Reports --------------------
def insert_report(user_id, reason="Misbehavior"):
    db.collection(REPORTS_COLLECTION).add({
        "user_id": user_id,
        "reason": reason,
        "report_date": datetime
    })
    print(f"✅ Report added for user_id={user_id} with reason='{reason}'")

# -------------------- Helper: Reset Auto-Increment (Firestore has no auto-increment) --------------------
def reset_autoincrement_id(collection_name):
    """Firestore uses auto-generated IDs. This is a placeholder."""
    print(f"⚠️ Firestore uses auto-generated IDs, reset_autoincrement_id not needed for '{collection_name}'")

# Read data
# (No implementation needed; Firestore uses auto-generated IDs)