from pymongo import MongoClient

print("Script started...")

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["nirmatriDB"]

    admins = db["superadmins"]

    admin = {
        "email": "admin@nirmatri.com",
        "password": "admin123",
        "role": "superadmin"
    }

    existing = admins.find_one({"email": "admin@nirmatri.com"})

    if existing:
        print("Admin already exists")
    else:
        admins.insert_one(admin)
        print("Superadmin created successfully")

except Exception as e:
    print("Error:", e)