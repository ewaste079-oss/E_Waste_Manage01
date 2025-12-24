from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from db import db, USERS_COLLECTION, EWASTE_COLLECTION, MESSAGES_COLLECTION
from auth import auth_bp
from admin import admin_bp
from analytics import get_summary, analytics_bp
from utils import send_email
import os, json, math, requests
from datetime import datetime
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'secret123'  # Replace this in production

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(analytics_bp)

# ------------------- GOOGLE MAPS HELPERS -------------------

def geocode_address(address, centres_cache=None):
    if centres_cache:
        for c in centres_cache:
            if c["address"] == address and "lat" in c and "lng" in c:
                return c["lat"], c["lng"]

    api_key = "YOUR_API_KEY"  # Replace with your real Google API Key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    res = requests.get(url).json()
    if res["status"] == "OK":
        loc = res["results"][0]["geometry"]["location"]
        lat, lng = loc["lat"], loc["lng"]
        if centres_cache is not None:
            for c in centres_cache:
                if c["address"] == address:
                    c["lat"] = lat
                    c["lng"] = lng
            centres_path = os.path.join("data", "centres.json")
            with open(centres_path, "w", encoding="utf-8") as f:
                json.dump(centres_cache, f, indent=2, ensure_ascii=False)
        return lat, lng
    return None, None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ------------------- ROUTES -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analytics')
def analytics_page():
    stats = get_summary()
    return render_template('analytics.html', stats=stats)

@app.route('/collection-centres')
def view_centres():
    json_path = os.path.join("data", "centres.json")
    with open(json_path, "r", encoding="utf-8") as f:
        centres = json.load(f)
    return render_template("collection_centres.html", centres=centres)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Please login to continue.", "warning")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    # ---------------- Add new E-waste ----------------
    if request.method == "POST":
        item_name = request.form["item_name"]
        category = request.form["category"]
        condition = request.form["condition"]
        weight = float(request.form["weight"])
        location = request.form["location"]

        # Get current UTC and convert to IST
        date_utc = datetime.utcnow()
        date_ist = date_utc + timedelta(hours=5, minutes=30)

        db.collection(EWASTE_COLLECTION).add({
            "user_id": user_id,
            "item_name": item_name,
            "category": category,
            "condition": condition,
            "weight": weight,
            "location": location,
            "date": date_ist
        })
        flash("E-waste entry submitted!", "success")

    # ---------------- Fetch user's E-waste ----------------
    ewaste_docs = db.collection(EWASTE_COLLECTION).where("user_id", "==", user_id).stream()
    my_data_enum = []
    for i, doc in enumerate(ewaste_docs, start=1):
        data = doc.to_dict()
        data["id"] = doc.id
        # Convert Firestore UTC to IST for display
        if data.get("date"):
            data["date_ist"] = data["date"].astimezone(tz=None) + timedelta(hours=5, minutes=30)
        my_data_enum.append((i, data))

    # Load centres.json
    centres_path = os.path.join("data", "centres.json")
    with open(centres_path, encoding="utf-8") as f:
        centres = json.load(f)

    return render_template("dashboard.html", my_data_enum=my_data_enum, centres=centres)

@app.route("/track/<string:waste_id>")
def track_waste(waste_id):
    if "user_id" not in session:
        return jsonify({"error": "Login required"})

    doc_ref = db.collection(EWASTE_COLLECTION).document(waste_id)
    doc = doc_ref.get()
    if not doc.exists:
        return jsonify({"error": "E-waste record not found"})

    waste = doc.to_dict()
    user_loc_text = waste.get("location", "")

    # Load centres.json
    centres_path = os.path.join("data", "centres.json")
    with open(centres_path, encoding="utf-8") as f:
        centres = json.load(f)

    user_lat, user_lng = geocode_address(user_loc_text)
    if not user_lat:
        return jsonify({"error": "Could not geocode user location"})

    nearest = None
    min_dist = float("inf")
    for c in centres:
        centre_lat, centre_lng = geocode_address(c["address"], centres)
        if centre_lat:
            d = haversine(user_lat, user_lng, centre_lat, centre_lng)
            if d < min_dist:
                min_dist = d
                nearest = c

    if not nearest:
        nearest = centres[0]

    return jsonify({
        "user_address": user_loc_text,
        "centre_address": nearest["address"]
    })

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # ---------------- Add message to Firestore ----------------
        db.collection(MESSAGES_COLLECTION).add({
            "name": name,
            "email": email,
            "message": message,
            "created_at": datetime.utcnow()
        })

        # Send email to admin
        subject = f"New Contact Form Message from {name}"
        body = f"""
           You have received a new message:

           Name: {name}
           Email: {email}
           Message: {message}
        """
        admin_email = "ewaste079@gmail.com"
        send_email(subject, body, admin_email)

        flash('Your message has been received. Our team will respond soon.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route("/predict", methods=["GET", "POST"])
def predict():
    predictions = None  # Default empty

    if request.method == "POST":
        try:
            # ---------------- Read form data ----------------
            brand_name = request.form.get("brand_name")
            device_age = float(request.form.get("Device_Age"))
            material_recovery = float(request.form.get("Material_Recovery_Rate"))
            year_of_manufacture = int(request.form.get("Year_of_Manufacture"))
            market_value = float(request.form.get("Market_Value_of_Metals"))
            cost_of_recovery = float(request.form.get("Cost_of_Recovery"))
            gold = float(request.form.get("Gold_g"))
            aluminum = float(request.form.get("Aluminum_g"))
            silver = float(request.form.get("Silver_g"))
            carbon = float(request.form.get("Carbon_g"))
            platinum = float(request.form.get("Platinum_g"))
            rhodium = float(request.form.get("Rhodium_g"))
            nickel = float(request.form.get("Nickel_g"))
            tin = float(request.form.get("Tin_g"))
            lithium = float(request.form.get("Lithium_g"))

            # ---------------- Dummy prediction ----------------
            # Replace this with your ML model logic
            predictions = {
    "Estimated Recovery Cost ($)": round(cost_of_recovery * 1.1, 2),
    "Estimated Scrap Value ($)": round(market_value * 0.8, 2),
    "Gold Content Value ($)": round(gold * 60, 2),          # $ per gram
    "Silver Content Value ($)": round(silver * 0.8, 2),     # $ per gram
    "Aluminum Content Value ($)": round(aluminum * 0.002, 2),
    "Platinum Content Value ($)": round(platinum * 30, 2),
    "Rhodium Content Value ($)": round(rhodium * 100, 2),
    "Nickel Content Value ($)": round(nickel * 2, 2),
    "Tin Content Value ($)": round(tin * 0.01, 2),
    "Lithium Content Value ($)": round(lithium * 5, 2),
    "Total Material Value ($)": round(
        gold*60 + silver*0.8 + aluminum*0.002 + platinum*30 +
        rhodium*100 + nickel*2 + tin*0.01 + lithium*5, 2
    ),
    "Recycling Score (%)": round(min(100, (material_recovery / device_age) * 10), 2)
}


        except Exception as e:
            flash(f"Error in prediction: {e}", "danger")

    return render_template("predict.html", predictions=predictions)



# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
