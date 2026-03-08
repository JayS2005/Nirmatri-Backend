import json
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
from apps.db.mongo import db
from bson import ObjectId

products = db["products"]
orders = db["orders"]
superadmins = db["superadmins"]
sellers = db["sellers"]

SECRET_KEY = "8f7d9c2a1b3e4f5a6c7d8e9f0a1b2c3d4"


# ==============================
# SUPERADMIN LOGIN
# ==============================

@csrf_exempt
def superadmin_login(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    data = json.loads(request.body)

    email = data.get("email")
    password = data.get("password")

    admin = superadmins.find_one({"email": email})

    if not admin:
        return JsonResponse({"error": "Admin not found"}, status=404)

    if admin["password"] != password:
        return JsonResponse({"error": "Invalid password"}, status=401)

    payload = {
        "admin_id": str(admin["_id"]),
        "email": admin["email"],
        "role": "superadmin",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return JsonResponse({
        "message": "Login successful",
        "token": token
    })

# ==============================
# GET ALL SELLERS
# ==============================

def all_sellers(request):

    data = list(sellers.find())

    for s in data:
        s["_id"] = str(s["_id"])

    return JsonResponse({"sellers": data})


# ==============================
# GET PENDING SELLERS
# ==============================

from django.views.decorators.http import require_GET, require_POST
from apps.db.mongo.db_collections import sellers_collection
from bson import ObjectId
from datetime import datetime
import json


# GET PENDING SELLERS FOR SUPERADMIN


@require_GET
def get_pending_sellers(request):


    data = list(sellers.find({"status": "pending"}))

    for s in data:
        s["_id"] = str(s["_id"])

    return JsonResponse({"pending_sellers": data})


# ==============================
# APPROVE SELLER
# ==============================
@csrf_exempt
def approve_seller(request, seller_id):

    sellers.update_one(
        {"_id": ObjectId(seller_id)},
        {"$set": {"status": "approved"}}
    )

    return JsonResponse({"message": "Seller approved"})
# ==============================
# REJECT SELLER
# ==============================

@csrf_exempt
def reject_seller(request, seller_id):

    sellers.update_one(
        {"_id": ObjectId(seller_id)},
        {"$set": {"status": "rejected"}}
    )

    return JsonResponse({"message": "Seller rejected"})

# ==============================
# ADMIN DASHBOARD
# ==============================

def admin_dashboard(request):

    total_sellers = sellers.count_documents({})
    pending_sellers = sellers.count_documents({"status": "pending"})
    total_products = products.count_documents({})

    revenue = 0
    for o in orders.find({}):
        revenue += o.get("amount", 0)

    return JsonResponse({
        "total_sellers": total_sellers,
        "pending_sellers": pending_sellers,
        "products": total_products,
        "revenue": revenue
    })

# ==============================
# RECENT ACTIVITIES FOR ADMIN DASHBOARD
# ==============================
def recent_activities(request):

    activities = []

    # New Sellers
    for s in sellers.find().sort("_id", -1).limit(3):
        activities.append({
            "action": "New seller registered",
            "time": "Recently",
            "status": "success"
        })

    # Approved Sellers
    for s in sellers.find({"status": "approved"}).sort("_id", -1).limit(2):
        activities.append({
            "action": "Seller approved",
            "time": "Recently",
            "status": "success"
        })

    # Orders
    for o in orders.find().sort("_id", -1).limit(2):
        activities.append({
            "action": "Payment processed",
            "time": "Recently",
            "status": "success"
        })

    return JsonResponse({"activities": activities})

    page = int(request.GET.get("page", 1))
    limit = 20
    skip = (page - 1) * limit

    sellers = list(
        sellers_collection.find(
            {
                "onboarding_completed": True,
                "status": "pending"
            },
            {"password": 0}
        ).skip(skip).limit(limit)
    )

    for seller in sellers:
        seller["_id"] = str(seller["_id"])

    return JsonResponse({
        "pending_sellers": sellers
    })

def pending_seller_count(request):

    count = sellers_collection.count_documents({
        "onboarding_completed": True,
        "status": "pending"
    })

    return JsonResponse({"count": count})

# APPROVE SELLER

@require_POST
def approve_seller(request):
    try:
        data = json.loads(request.body)
        seller_id = data.get("seller_id")

        sellers_collection.update_one(
            {"_id": ObjectId(seller_id)},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": datetime.utcnow(),
                    "approved_by": "superadmin"
                }
            }
        )

        return JsonResponse({"message": "Seller approved"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ======================================
# REJECT SELLER
# ======================================

@require_POST
def reject_seller(request):
    try:
        data = json.loads(request.body)
        seller_id = data.get("seller_id")

        sellers_collection.update_one(
            {"_id": ObjectId(seller_id)},
            {
                "$set": {
                    "status": "rejected"
                }
            }
        )

        return JsonResponse({"message": "Seller rejected"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ======================================
# SUSPEND SELLER
# ======================================

@require_POST
def suspend_seller(request):
    try:
        data = json.loads(request.body)
        seller_id = data.get("seller_id")

        sellers_collection.update_one(
            {"_id": ObjectId(seller_id)},
            {
                "$set": {
                    "status": "suspended"
                }
            }
        )

        return JsonResponse({"message": "Seller suspended"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

