import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
import pickle
import os

# ---------------- LOAD DATASET ----------------
df = pd.read_csv(r"C:\Users\Pranav Kadam\OneDrive\Attachments\Desktop\E_WASTE\data\updated_e_waste_dataset.csv")

# 🔧 Strip whitespace from column names (avoid hidden errors)
df.columns = df.columns.str.strip()

# Drop unnecessary column
df = df.drop(columns=["Item Name"], errors='ignore')

# ---------------- ENCODE CATEGORICAL COLUMNS ----------------
label_encoders = {}
for col in df.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# ---------------- FEATURES (X) ----------------
X = df.drop(columns=[
    'Category', 'Device Type', 'Device Condition',
    'Recycling Score', 'Profit', 'Current Metal Value ($)'
])

# ---------------- CREATE MODELS DIR ----------------
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)

# ---------------- CLASSIFICATION ----------------
classification_targets = ['Category', 'Device Type', 'Device Condition', 'Recycling Score']

for target in classification_targets:
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[Classification] {target} Accuracy: {acc:.2%}")

    with open(os.path.join(model_dir, f"{target.replace(' ', '_').lower()}_model.pkl"), 'wb') as f:
        pickle.dump(clf, f)

# ---------------- REGRESSION ----------------
regression_targets = ['Profit', 'Current Metal Value ($)']

for target in regression_targets:
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_train, y_train)

    y_pred = reg.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"[Regression] {target} MSE: {mse:.2f}")

    with open(os.path.join(model_dir, f"{target.replace(' ', '_').lower()}_model.pkl"), 'wb') as f:
        pickle.dump(reg, f)

# ---------------- SAVE LABEL ENCODERS ----------------
with open(os.path.join(model_dir, "label_encoders.pkl"), "wb") as f:
    pickle.dump(label_encoders, f)

print("\n✅ All models & encoders trained and saved in 'models/' folder.")
