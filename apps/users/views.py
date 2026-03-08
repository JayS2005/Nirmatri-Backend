import json
import token
import bcrypt
import jwt

from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from bson import ObjectId
from apps.db.mongo.connection import users_collection
from apps.users.utils import create_jwt_token


# ================= USER LOGIN =================
@csrf_exempt
def user_login(request):

    if request.method == "POST":
        data = json.loads(request.body)

        email = data.get("email")
        password = data.get("password")

        user = users_collection.find_one({"email": email})

        if not user:
            return JsonResponse({"message": "User not found"}, status=404)

        if not bcrypt.checkpw(password.encode(), user["password"].encode()):
            return JsonResponse({"message": "Invalid password"}, status=401)

        token = create_jwt_token(str(user["_id"]))

        return JsonResponse({
            "token": token,
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "gender": user.get("gender"),

            }
        })

    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def user_register(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")


        if not name or not email or not password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return JsonResponse({"error": "User already exists"}, status=400)

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Insert user
        result = users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password.decode(),
            "gender": "",
            "mobile": ""
        })

        user_id = str(result.inserted_id)

        # Create JWT
        token = create_jwt_token(user_id)

        return JsonResponse({
            "message": "User registered successfully",
            "token": token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "phone": "",
                "gender": "",
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ================= GET PROFILE =================
@csrf_exempt
def get_profile(request):
    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"error": "Authorization header missing"}, status=401)

        if not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Invalid token format"}, status=401)

        token = auth_header.split(" ")[1]

        # Decode JWT
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print("DECODED TOKEN:", decoded)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        user_id = decoded.get("user_id")

        if not user_id:
            return JsonResponse({"error": "Invalid token payload"}, status=401)

        try:
            user_obj_id = ObjectId(user_id)
        except Exception:
            return JsonResponse({"error": "Invalid user id"}, status=400)

        user = users_collection.find_one({"_id": user_obj_id})

        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        return JsonResponse({
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email"),
            "phone": user.get("mobile"),
            "gender": user.get("gender"),
        })

    except Exception as e:
        print("PROFILE ERROR:", str(e))
        return JsonResponse({"error": "Server error"}, status=500)


# ================= UPDATE PROFILE =================
@csrf_exempt
def update_profile(request):

    if request.method == "PUT":

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"error": "Token missing"}, status=401)

        token = auth_header.split(" ")[1]

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")

        data = json.loads(request.body)

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )

        return JsonResponse({"message": "Profile updated successfully"})

    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def logout_user(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JsonResponse({"error": "Authorization header missing"}, status=401)

        token = auth_header.split(" ")[1]

        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")

        print("DECODED TOKEN:", decoded)

        user_obj_id = ObjectId(user_id)

        users_collection.update_one(
            {"_id": user_obj_id},
            {"$set": {"is_active": False}}
        )

        return JsonResponse({"message": "User logged out successfully"})

    except Exception as e:
        print("LOGOUT ERROR:", str(e))
        return JsonResponse({"error": "Server error"}, status=500)


# ================= FORGOT PASSWORD =================
@csrf_exempt
def forgot_password(request):
    return JsonResponse({"message": "Forgot password API working"})


# ================= RESET PASSWORD =================
@csrf_exempt
def reset_password(request):
    return JsonResponse({"message": "Reset password API working"})