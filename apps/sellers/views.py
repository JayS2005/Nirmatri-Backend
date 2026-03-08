#Seller Register API
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.db.mongo.db_collections import sellers_collection
from apps.sellers.services import seller_login_service
from datetime import datetime


#register API
@csrf_exempt
def seller_login(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=405)

    data = json.loads(request.body)

    response, status = seller_login_service(data)

    return JsonResponse(response, status=status)

@csrf_exempt
@require_POST
def seller_register(request):
    try:
        data = json.loads(request.body)

        fullname = data.get("fullname")
        email = data.get("email")
        password = data.get("password")

        # ================= VALIDATION =================
        missing = []
        for field in ["fullname", "email", "password"]:
            if not data.get(field):
                missing.append(field)

        if missing:
            return JsonResponse(
                {"error": "Missing fields", "fields": missing},
                status=400
            )

        # ================= DUPLICATE CHECK =================
        if sellers_collection.find_one({"email": email}):
            return JsonResponse(
                {"error": "Seller already registered with this email"},
                status=409
            )

        # ================= SAVE TO DB =================
        seller_doc = {

            # ===== BASIC INFO =====
            "full_name": fullname,
            "email": email,
            "password": password,

            # ===== STORE INFO =====
            "store_name": None,
            "owner_name": None,
            "store_category": [],

            # ===== KYC =====
            "pan_number": None,
            "aadhaar_number": None,

            # ===== BANK =====
            "bank_name": None,
            "account_holder": None,
            "account_number": None,
            "ifsc_code": None,

            # ===== CONTACT =====
            "phone_number": None,

            # ===== WORKFLOW STATUS =====
            "onboarding_completed": False,

            # seller status controlled by admin
            "status": "draft",     
            # draft → onboarding not completed
            # pending → waiting admin review
            # approved → seller active
            # rejected → seller rejected
            # suspended → seller blocked

            # ===== ADMIN ACTION =====
            "approved_at": None,
            "approved_by": None,

            # ===== TIMESTAMPS =====
            "created_at": datetime.utcnow()
        }

        sellers_collection.insert_one(seller_doc)

        return JsonResponse(
            {
                "message": "Seller registered successfully",
                "status": "pending",
                "note": "Your account will be activated after admin approval"
            },
            status=201
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        print("SELLER REGISTER ERROR:", str(e))
        return JsonResponse(
            {"error": "Server error", "details": str(e)},
            status=500
        )

#=======seller onboarding API========

@csrf_exempt
def seller_onboarding(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)

        email = data.get("email")

        sellers_collection.update_one(
            {"email": email},
            {
                "$set": {

                    # STORE INFO
                    "store_name": data.get("storeName"),
                    "owner_name": data.get("ownerName"),
                    "store_category": data.get("storeCategory"),

                    # KYC
                    "pan_number": data.get("panNumber"),
                    "pan_Document": data.get("panDocument"),
                    "aadhaar_number": data.get("adharNumber"),
                    "adhar_document": data.get("adharDocument"),

                    # BANK
                    "account_holder": data.get("accountHolderName"),
                    "account_number": data.get("accountNumber"),
                    "ifsc_code": data.get("ifscCode"),
                    "bank_name": data.get("bankName"),

                    # PHONE
                    "phone_number": data.get("phoneNumber"),
                    "otp": data.get("otp"),
                    "isOtpVerified": False,
                    # STATUS
                    "onboarding_completed": True,
                    "status": "pending"
                }
            }
        )

        return JsonResponse({
            "message": "Onboarding completed",
            "status": "pending_approval"
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    


@csrf_exempt
def approve_seller(request):
    
    data = json.loads(request.body)

    email = data.get("email")

    sellers_collection.update_one(
    {"email": email},
    {
        "$set": {
            "status": "approved",
            "approved_at": datetime.utcnow(),
            "approved_by": "admin_id"
        }
    }
)

    return JsonResponse({"message": "seller approved"})


def reject_seller(email):

    sellers_collection.update_one(
    {"email": email},
    {
        "$set": {
            "status": "rejected"
        }
    }
)

def suspend(email): 
    sellers_collection.update_one(
    {"email": email},
    {
        "$set": {
            "status": "suspended"
        }
    }
)