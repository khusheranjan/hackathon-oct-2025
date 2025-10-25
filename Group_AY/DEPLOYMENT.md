# Setup and Deployment Guide

## Quick Start (Local Development)

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    texlive \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-science \
    texlive-latex-recommended \
    cm-super \
    dvipng
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 ffmpeg
brew install --cask mactex
```

#### Windows
1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
3. Install MiKTeX from [miktex.org](https://miktex.org/download)

### 2. Clone/Download the Project

```bash
git clone <your-repo-url>
cd ai-video-generator
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

Or use a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Set Your OpenAI API Key

```bash
# Linux/macOS
export OPENAI_API_KEY='your-api-key-here'

# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY='your-api-key-here'
```

Or create a `.env` file:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 5. Test the Installation

```bash
# Test basic generation
python video_generator.py

# Or run an example
python examples.py 1
```

## Docker Deployment

### Using Docker

1. **Build the image:**
```bash
docker build -t ai-video-generator .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 \
    -e OPENAI_API_KEY='your-api-key' \
    -v $(pwd)/outputs:/app/outputs \
    ai-video-generator
```

### Using Docker Compose

1. **Create a `.env` file:**
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

2. **Start the services:**
```bash
docker-compose up -d
```

3. **Check logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

## Production Deployment

### Option 1: Deploy to AWS EC2

1. **Launch an EC2 instance** (t3.large or larger recommended)

2. **SSH into the instance:**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. **Install Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

4. **Clone and deploy:**
```bash
git clone <your-repo>
cd ai-video-generator
echo "OPENAI_API_KEY=your-key" > .env
docker-compose up -d
```

5. **Configure security group** to allow port 5000

### Option 2: Deploy to Google Cloud Run

1. **Build and push to Container Registry:**
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-video-generator
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy ai-video-generator \
    --image gcr.io/YOUR_PROJECT_ID/ai-video-generator \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars OPENAI_API_KEY=your-key \
    --memory 4Gi \
    --timeout 900
```

### Option 3: Deploy to Heroku

1. **Create a Heroku app:**
```bash
heroku create your-app-name
```

2. **Set environment variables:**
```bash
heroku config:set OPENAI_API_KEY=your-key
```

3. **Deploy:**
```bash
git push heroku main
```

### Option 4: Deploy to Railway

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Login and initialize:**
```bash
railway login
railway init
```

3. **Set environment variables:**
```bash
railway variables set OPENAI_API_KEY=your-key
```

4. **Deploy:**
```bash
railway up
```

## Nginx Reverse Proxy Setup

If you want to expose the API on port 80/443 with SSL:

1. **Install Nginx:**
```bash
sudo apt install nginx certbot python3-certbot-nginx
```

2. **Create Nginx config** (`/etc/nginx/sites-available/video-generator`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 900s;
    }
}
```

3. **Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/video-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Get SSL certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

## Scaling for Production

### 1. Use Redis for Job Queue

Install Redis and modify `api_server.py` to use Redis instead of in-memory dict:

```bash
pip install redis rq
```

### 2. Set Up Worker Processes

Use Gunicorn for the API:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### 3. Add Background Workers

Create a worker process for video generation:
```python
# worker.py
from rq import Worker, Queue, Connection
import redis

listen = ['default']
redis_conn = redis.from_url('redis://localhost:6379')

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
```

Run workers:
```bash
python worker.py
```

### 4. Use S3 for Output Storage

Store generated videos in S3 instead of local filesystem:
```bash
pip install boto3
```

### 5. Add Rate Limiting

Use Flask-Limiter:
```bash
pip install flask-limiter
```

## Monitoring and Logging

### Set up logging

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### Monitor with Prometheus

Add metrics endpoint:
```bash
pip install prometheus-flask-exporter
```

### Use Sentry for Error Tracking

```bash
pip install sentry-sdk[flask]
```

## Troubleshooting Production Issues

### High Memory Usage
- Limit concurrent jobs
- Use worker queue system
- Increase instance size
- Clean up outputs regularly

### Slow Generation
- Use faster GPT models (gpt-3.5-turbo)
- Reduce video quality for drafts
- Cache common animations
- Use dedicated GPU instances

### API Timeouts
- Increase timeout limits in Nginx/load balancer
- Use async job processing
- Return job ID immediately, process in background

### Storage Issues
- Implement automatic cleanup of old videos
- Use cloud storage (S3, GCS)
- Compress output videos
- Stream videos instead of storing locally

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Rate limit API endpoints** - Prevent abuse
3. **Validate user inputs** - Prevent code injection
4. **Use HTTPS** - Encrypt data in transit
5. **Implement authentication** - Protect API endpoints
6. **Sanitize file paths** - Prevent directory traversal
7. **Run in containers** - Isolate processes
8. **Keep dependencies updated** - Security patches
9. **Log security events** - Monitor for attacks
10. **Set up firewall rules** - Restrict access

## Performance Optimization

### Caching Strategies

1. **Cache Manim scenes** - Reuse common animations
2. **Cache audio files** - Store generated speech
3. **Cache API responses** - Reduce OpenAI calls

### Optimization Tips

1. **Use lower quality for previews** - Faster iteration
2. **Parallel processing** - Generate audio while rendering
3. **Optimize Manim code** - Reduce complexity
4. **Use CDN for outputs** - Fast video delivery
5. **Implement job priorities** - Handle urgent requests first

## Backup and Recovery

### Backup Strategy

```bash
# Backup outputs
tar -czf outputs-backup-$(date +%Y%m%d).tar.gz outputs/

# Upload to S3
aws s3 cp outputs-backup-*.tar.gz s3://your-bucket/backups/
```

### Disaster Recovery

1. Keep infrastructure as code (Terraform/CloudFormation)
2. Automate deployments (CI/CD)
3. Regular backups of data
4. Document recovery procedures
5. Test recovery process regularly

## Cost Optimization

### OpenAI API Costs
- Use gpt-3.5-turbo for simpler content ($0.002/1K tokens vs $0.03/1K for GPT-4)
- Use tts-1 instead of tts-1-hd for drafts ($0.015/1K chars vs $0.03/1K)
- Cache responses when possible
- Set token limits

### Infrastructure Costs
- Use spot instances for workers (70% cheaper)
- Auto-scale based on demand
- Use serverless for API (pay per use)
- Optimize storage (lifecycle policies)
- Use reserved instances for steady load

## Getting Help

- GitHub Issues: Report bugs and request features
- Documentation: Check the README for details
- Community: Join discussions
- Email: support@your-domain.com

---

Last updated: 2025
