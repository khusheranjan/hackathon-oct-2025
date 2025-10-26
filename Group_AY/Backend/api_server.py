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

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Store job status
jobs = {}

def generate_video_async(job_id: str, description: str, project_name: str, api_key: str = None, elevenlabs_api_key: str = None):
    """
    Run video generation in background thread
    """
    try:
        jobs[job_id]['status'] = 'processing'
        # API keys will be loaded from .env if not provided
        generator = EducationalVideoGenerator(api_key, elevenlabs_api_key=elevenlabs_api_key, output_dir=f"outputs/{job_id}")
        results = generator.generate_video(description, project_name)

        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['results'] = results

    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)


@app.route('/api/generate', methods=['POST'])
def generate_video():
    """
    POST endpoint to start video generation

    Request body:
    {
        "description": "Natural language description of the educational content",
        "project_name": "optional_project_name",
        "openai_api_key": "your-openai-api-key (optional if set in .env)",
        "elevenlabs_api_key": "your-elevenlabs-api-key (optional if set in .env)"
    }
    """
    data = request.json

    if not data or 'description' not in data:
        return jsonify({'error': 'Missing description field'}), 400

    description = data['description']
    project_name = data.get('project_name', 'video_' + uuid.uuid4().hex[:8])
    # API keys are optional if they're set in .env
    api_key = data.get('openai_api_key')
    elevenlabs_api_key = data.get('elevenlabs_api_key')

    # Create job ID
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        'status': 'queued',
        'description': description,
        'project_name': project_name
    }

    # Start background thread
    thread = threading.Thread(
        target=generate_video_async,
        args=(job_id, description, project_name, api_key, elevenlabs_api_key)
    )
    thread.start()

    return jsonify({
        'job_id': job_id,
        'status': 'queued',
        'message': 'Video generation started'
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


if __name__ == '__main__':
    # Create outputs directory
    Path('outputs').mkdir(exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
