import sqlite3

# Connect to the database
conn = sqlite3.connect("users.db")  # Ensure the correct path if `users.db` is elsewhere
cursor = conn.cursor()

# Check if the table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Retrieve user data
cursor.execute("SELECT * FROM user;")  # Make sure 'user' is the correct table name
users = cursor.fetchall()

print("\nUsers in Database:")
for user in users:
    print(user)

# Close the connection
conn.close()
