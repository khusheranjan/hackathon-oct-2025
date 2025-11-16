"""
Flask API wrapper for the Educational Video Generator
Allows users to submit requests via HTTP
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from pathlib import Path
import threading
from video_generator import EducationalVideoGenerator
from dotenv import load_dotenv
from auth import verify_google_token, create_jwt_token, decode_jwt_token, require_auth, store_user
from chat_manager import (
    create_chat_session,
    get_chat_session,
    get_user_chats,
    update_chat_title,
    delete_chat_session,
    add_message_to_chat,
    get_chat_messages,
    clear_chat_messages
)
from database import connect_to_mongodb, close_connection, get_users_collection
from payment_routes import payment_bp
from subscription_manager import check_can_generate_video, increment_usage, get_user_subscription_info
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Register payment blueprint
app.register_blueprint(payment_bp)

# Initialize MongoDB connection on startup
try:
    connect_to_mongodb()
    logger.info("MongoDB connected successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    # You might want to exit here in production
    # raise

# Store job status
jobs = {}

def generate_video_async(
    job_id: str,
    description: str,
    project_name: str,
    api_key: str = None,
    elevenlabs_api_key: str = None,
    add_avatar: bool = False,
    avatar_position: str = "bottom-right",
    use_simple_avatar: bool = True,
    enhance_prompt: bool = True,
    user_id: str = None,
    use_credit: bool = False
):
    """
    Run video generation in background thread
    """
    try:
        jobs[job_id]['status'] = 'processing'
        # API keys will be loaded from .env if not provided
        generator = EducationalVideoGenerator(api_key, elevenlabs_api_key=elevenlabs_api_key, output_dir=f"outputs/{job_id}")
        results = generator.generate_video(
            description,
            project_name,
            add_avatar=add_avatar,
            avatar_position=avatar_position,
            use_simple_avatar=use_simple_avatar,
            enhance_prompt=enhance_prompt
        )

        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['results'] = results

        # Increment usage or deduct credit after successful generation
        if user_id:
            increment_usage(user_id, used_credit=use_credit)

    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)


@app.route('/api/generate', methods=['POST'])
@require_auth
def generate_video():
    """
    POST endpoint to start video generation (now requires authentication)

    Request body:
    {
        "description": "Natural language description of the educational content",
        "project_name": "optional_project_name",
        "openai_api_key": "your-openai-api-key (optional if set in .env)",
        "elevenlabs_api_key": "your-elevenlabs-api-key (optional if set in .env)",
        "add_avatar": false,
        "avatar_position": "bottom-right",
        "use_simple_avatar": true,
        "enhance_prompt": true,
        "duration": 60 (estimated duration in seconds)
    }
    """
    data = request.json

    if not data or 'description' not in data:
        return jsonify({'error': 'Missing description field'}), 400

    user_id = request.user.get('user_id')
    description = data['description']
    project_name = data.get('project_name', 'video_' + uuid.uuid4().hex[:8])
    # API keys are optional if they're set in .env
    api_key = data.get('openai_api_key')
    elevenlabs_api_key = data.get('elevenlabs_api_key')

    # Avatar options
    add_avatar = data.get('add_avatar', False)
    avatar_position = data.get('avatar_position', 'bottom-right')
    use_simple_avatar = data.get('use_simple_avatar', True)

    # Prompt enhancement option (default: True)
    enhance_prompt = data.get('enhance_prompt', True)

    # Video duration estimate (for limit checking)
    duration = data.get('duration', 60)

    # Check if user can generate video
    can_generate, reason = check_can_generate_video(user_id, duration, add_avatar)

    if not can_generate:
        return jsonify({
            'error': reason,
            'subscription_required': True
        }), 403

    # Determine if using credit
    use_credit = reason == "Using credit"

    # Create job ID
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        'status': 'queued',
        'description': description,
        'project_name': project_name,
        'add_avatar': add_avatar,
        'enhance_prompt': enhance_prompt,
        'user_id': user_id
    }

    # Start background thread
    thread = threading.Thread(
        target=generate_video_async,
        args=(job_id, description, project_name, api_key, elevenlabs_api_key, add_avatar, avatar_position, use_simple_avatar, enhance_prompt, user_id, use_credit)
    )
    thread.start()

    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Video generation started',
        'avatar_enabled': add_avatar,
        'prompt_enhancement': enhance_prompt,
        'using_credit': use_credit
    }), 202


@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """
    GET endpoint to check job status
    """
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    response = {
        'job_id': job_id,
        'status': job['status'],
        'project_name': job['project_name']
    }
    
    if job['status'] == 'completed':
        response['results'] = job['results']
        response['download_url'] = f"/api/download/{job_id}"
    elif job['status'] == 'failed':
        response['error'] = job.get('error', 'Unknown error')
    
    return jsonify(response)


@app.route('/api/download/<job_id>', methods=['GET'])
def download_video(job_id):
    """
    GET endpoint to download the final video
    """
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Video not ready yet'}), 400
    
    video_path = job['results']['final_video']
    
    if not os.path.exists(video_path):
        return jsonify({'error': 'Video file not found'}), 404
    
    return send_file(
        video_path,
        mimetype='video/mp4',
        as_attachment=True,
        download_name=f"{job['project_name']}.mp4"
    )


@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    """
    GET endpoint to list all jobs
    """
    return jsonify({
        'jobs': [
            {
                'job_id': job_id,
                'status': job['status'],
                'project_name': job['project_name']
            }
            for job_id, job in jobs.items()
        ]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'})


# Authentication endpoints
@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """
    POST endpoint for Google OAuth authentication

    Request body:
    {
        "token": "google-oauth-token"
    }
    """
    data = request.json

    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token field'}), 400

    google_token = data['token']
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')

    if not google_client_id:
        return jsonify({'error': 'Google OAuth not configured'}), 500

    try:
        # Verify Google token
        user_data = verify_google_token(google_token, google_client_id)

        # Store user in database
        stored_user = store_user(user_data)

        # Create JWT token
        jwt_token = create_jwt_token(user_data)

        return jsonify({
            'token': jwt_token,
            'user': {
                'email': stored_user['email'],
                'name': stored_user['name'],
                'picture': stored_user['picture']
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 401


@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_token():
    """
    GET endpoint to verify JWT token
    Protected route example
    """
    return jsonify({
        'user': {
            'email': request.user['email'],
            'name': request.user['name']
        }
    }), 200


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    GET endpoint to get current user info with subscription details
    """
    user_id = request.user['user_id']
    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"google_id": user_id})

    if not user_doc:
        return jsonify({'error': 'User not found'}), 404

    # Get subscription info
    subscription_info = get_user_subscription_info(user_id)

    return jsonify({
        'user': {
            'email': request.user['email'],
            'name': request.user['name'],
            'user_id': request.user['user_id'],
            'picture': user_doc.get('picture', ''),
            'subscription': subscription_info
        }
    }), 200


# Chat session endpoints
@app.route('/api/chats', methods=['GET'])
@require_auth
def list_chats():
    """
    GET endpoint to list all chat sessions for the current user
    """
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    user_id = request.user['user_id']
    chats = get_user_chats(user_id, limit, offset)

    return jsonify({'chats': chats}), 200


@app.route('/api/chats', methods=['POST'])
@require_auth
def create_chat():
    """
    POST endpoint to create a new chat session

    Request body:
    {
        "title": "Optional chat title"
    }
    """
    data = request.json or {}
    title = data.get('title', 'New Chat')

    user_id = request.user['user_id']
    chat = create_chat_session(user_id, title)

    return jsonify({'chat': chat}), 201


@app.route('/api/chats/<chat_id>', methods=['GET'])
@require_auth
def get_chat(chat_id):
    """
    GET endpoint to get a specific chat session with all messages
    """
    user_id = request.user['user_id']
    chat = get_chat_session(chat_id, user_id)

    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({'chat': chat}), 200


@app.route('/api/chats/<chat_id>', methods=['PATCH'])
@require_auth
def update_chat(chat_id):
    """
    PATCH endpoint to update chat title

    Request body:
    {
        "title": "New chat title"
    }
    """
    data = request.json

    if not data or 'title' not in data:
        return jsonify({'error': 'Missing title field'}), 400

    user_id = request.user['user_id']
    chat = update_chat_title(chat_id, user_id, data['title'])

    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({'chat': chat}), 200


@app.route('/api/chats/<chat_id>', methods=['DELETE'])
@require_auth
def delete_chat(chat_id):
    """
    DELETE endpoint to delete a chat session
    """
    user_id = request.user['user_id']
    success = delete_chat_session(chat_id, user_id)

    if not success:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({'message': 'Chat deleted successfully'}), 200


@app.route('/api/chats/<chat_id>/messages', methods=['POST'])
@require_auth
def add_chat_message(chat_id):
    """
    POST endpoint to add a message to a chat session

    Request body:
    {
        "role": "user" or "assistant",
        "content": "message content"
    }
    """
    data = request.json

    if not data or 'role' not in data or 'content' not in data:
        return jsonify({'error': 'Missing role or content field'}), 400

    user_id = request.user['user_id']
    message = {
        'role': data['role'],
        'content': data['content']
    }

    chat = add_message_to_chat(chat_id, user_id, message)

    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({'chat': chat}), 200


@app.route('/api/chats/<chat_id>/messages', methods=['GET'])
@require_auth
def get_chat_messages_endpoint(chat_id):
    """
    GET endpoint to get all messages from a chat session
    """
    user_id = request.user['user_id']
    messages = get_chat_messages(chat_id, user_id)

    if messages is None:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({'messages': messages}), 200


@app.route('/api/chats/<chat_id>/clear', methods=['POST'])
@require_auth
def clear_chat(chat_id):
    """
    POST endpoint to clear all messages from a chat session
    """
    user_id = request.user['user_id']
    chat = clear_chat_messages(chat_id, user_id)

    if not chat:
        return jsonify({'error': 'Chat not found'}), 404

    return jsonify({'chat': chat}), 200


if __name__ == '__main__':
    # Create outputs directory
    Path('outputs').mkdir(exist_ok=True)

    try:
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        # Close MongoDB connection on shutdown
        close_connection()
        logger.info("Application shutdown")
