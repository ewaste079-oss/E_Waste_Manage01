from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from db import db, EWASTE_COLLECTION
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')
GRAPH_DIR = "static/graphs"
os.makedirs(GRAPH_DIR, exist_ok=True)

# ------------------- LOAD DATA FROM FIRESTORE -------------------
def load_ewaste_data(user_id=None, is_admin=False):
    docs = db.collection(EWASTE_COLLECTION).stream()
    data = []
    for doc in docs:
        d = doc.to_dict() | {"id": doc.id}
        if is_admin or (user_id and d.get("user_id") == user_id):
            data.append(d)
    return pd.DataFrame(data)


# ------------------- SUMMARY -------------------
def get_summary(user_id=None, is_admin=False):
    df = load_ewaste_data(user_id, is_admin)
    if df.empty:
        return {}
    return {
        'Total Records': len(df),
        'Total Weight (kg)': df['weight'].sum(),
        'Unique Locations': df['location'].nunique()
    }


# ------------------- MAP DATA -------------------
@analytics_bp.route('/map-data')
def map_data():
    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    df = load_ewaste_data(user_id, is_admin)
    if df.empty:
        return jsonify([])

    result = []
    grouped = df.groupby('location')['weight'].sum().reset_index()
    for _, row in grouped.iterrows():
        location = f"{row['location']}, Maharashtra, India"
        weight = row['weight']
        try:
            res = requests.get(f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1",
                               headers={'User-Agent': 'E-Waste-Map'}).json()
            lat, lon = (float(res[0]['lat']), float(res[0]['lon'])) if res else (19.9975, 73.7898)
        except:
            lat, lon = 19.9975, 73.7898
        result.append({"location": row['location'], "lat": lat, "lng": lon, "weight": weight})
    return jsonify(result)


# ------------------- ANALYTICS PAGE -------------------
@analytics_bp.route('/')
def show_analytics():
    if 'user_id' not in session:
        flash('Login required to view analytics', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    is_admin = session.get('is_admin', False)
    df = load_ewaste_data(user_id, is_admin)

    if df.empty:
        flash('No data available for analytics', 'info')
        return render_template('analytics.html', graphs=[], summary={})

    summary = get_summary(user_id, is_admin)
    graphs = []

    # Bar Chart - Category
    try:
        cat_graph = os.path.join(GRAPH_DIR, "category.jpg")
        df.groupby('category')['weight'].sum().plot(kind='bar', color='skyblue',
                                                    title='E-Waste by Category',
                                                    xlabel='Category', ylabel='Total Weight (kg)')
        plt.tight_layout()
        plt.savefig(cat_graph)
        plt.clf()
        graphs.append('graphs/category.jpg')
    except Exception as e:
        print("❌ Category graph error:", e)

    # Pie Chart - Location
    try:
        loc_graph = os.path.join(GRAPH_DIR, "location.jpg")
        df['location'].value_counts().plot(kind='pie', autopct='%1.1f%%', title='E-Waste by Location')
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(loc_graph)
        plt.clf()
        graphs.append('graphs/location.jpg')
    except Exception as e:
        print("❌ Location graph error:", e)

    # Line Chart - Monthly Trend
    try:
        df['date'] = pd.to_datetime(df['date'])
        monthly_graph = os.path.join(GRAPH_DIR, "monthly.jpg")
        df.groupby(df['date'].dt.to_period('M'))['weight'].sum().plot(kind='line', marker='o', title='Monthly E-Waste Trend')
        plt.xlabel('Month')
        plt.ylabel('Weight (kg)')
        plt.tight_layout()
        plt.savefig(monthly_graph)
        plt.clf()
        graphs.append('graphs/monthly.jpg')
    except Exception as e:
        print("❌ Monthly trend graph error:", e)

    return render_template('analytics.html', graphs=graphs, summary=summary)
