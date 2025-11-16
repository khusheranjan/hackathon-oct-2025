"""
Authentication module for Google OAuth
"""

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify
from database import get_users_collection
from models import User

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


def verify_google_token(token: str, client_id: str) -> dict:
    """
    Verify Google OAuth token and return user info
    """
    try:
        # Allow 60 seconds of clock skew to handle time sync issues
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id,
            clock_skew_in_seconds=60
        )

        # Verify the token is for our app
        if idinfo['aud'] != client_id:
            raise ValueError('Invalid audience')

        return {
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'sub': idinfo['sub']  # Google user ID
        }
    except ValueError as e:
        raise ValueError(f'Invalid token: {str(e)}')


def create_jwt_token(user_data: dict) -> str:
    """
    Create JWT token for authenticated user
    """
    payload = {
        'user_id': user_data['sub'],
        'email': user_data['email'],
        'name': user_data['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    """
    Decode and verify JWT token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')


def require_auth(f):
    """
    Decorator to protect routes that require authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401

        try:
            # Expected format: "Bearer <token>"
            token = auth_header.split(' ')[1]
            user_data = decode_jwt_token(token)

            # Attach user data to request for use in route
            request.user = user_data

            return f(*args, **kwargs)
        except (IndexError, ValueError) as e:
            return jsonify({'error': str(e)}), 401

    return decorated_function


def store_user(user_data: dict):
    """
    Store user in MongoDB database
    """
    users_collection = get_users_collection()
    google_id = user_data['sub']

    # Check if user already exists
    existing_user = users_collection.find_one({"google_id": google_id})

    if existing_user:
        # Update existing user
        users_collection.update_one(
            {"google_id": google_id},
            {
                "$set": {
                    "name": user_data['name'],
                    "picture": user_data.get('picture', ''),
                    "updated_at": datetime.datetime.utcnow()
                }
            }
        )
        return User.to_dict(users_collection.find_one({"google_id": google_id}))
    else:
        # Create new user
        new_user = User.create(
            google_id=google_id,
            email=user_data['email'],
            name=user_data['name'],
            picture=user_data.get('picture', '')
        )
        result = users_collection.insert_one(new_user)
        new_user['_id'] = result.inserted_id
        return User.to_dict(new_user)


def get_user(google_id: str):
    """
    Get user from database by Google ID
    """
    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"google_id": google_id})
    return User.to_dict(user_doc) if user_doc else None
