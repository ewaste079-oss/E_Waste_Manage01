import sqlite3

# Path to your database
DB_PATH = "data/ewaste.db"  # Change if your DB is in a different location

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Step 1: Add role column if it doesn't already exist
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    print("✅ 'role' column added to users table.")
except sqlite3.OperationalError:
    print("ℹ️ 'role' column already exists. Skipping ALTER TABLE.")

# Step 2: Set the role for your admin account
admin_email = "pranavk9699@gmail.com"  # Change this to your real admin email
cursor.execute("UPDATE users SET role = 'admin' WHERE email = ?", (admin_email,))
if cursor.rowcount > 0:
    print(f"✅ Admin role set for {admin_email}")
else:
    print(f"⚠️ No user found with email {admin_email}")

# Save changes and close connection
conn.commit()
conn.close()

print("✅ Database update complete.")
