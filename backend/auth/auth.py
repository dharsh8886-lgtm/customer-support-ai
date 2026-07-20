import bcrypt
from database.mongodb import users_collection
from auth.jwt_handler import create_access_token


def register_user(name, email, password):
    existing_user = users_collection.find_one({"email": email})

    if existing_user:
        return {
            "success": False,
            "message": "Email already registered."
        }

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password
    })

    return {
        "success": True,
        "message": "Registration successful."
    }


def login_user(email, password):
    user = users_collection.find_one({"email": email})

    if not user:
        return {
            "success": False,
            "message": "User not found."
        }

    if bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        token = create_access_token(email)

        return {
            "success": True,
            "message": "Login successful.",
            "access_token": token,
            "name": user.get("name", "User"),
            "email": user.get("email", email)
        }

    return {
        "success": False,
        "message": "Invalid password."
    }
