# Quick Start Guide - EduVideo AI with MongoDB

## What's New?

✅ MongoDB database for persistent storage
✅ All chats and messages saved permanently
✅ Data survives server restarts
✅ Production-ready architecture

## Running the Application

### Prerequisites

- Docker and Docker Compose installed
- Google OAuth Client ID (see SETUP_AUTH.md)
- API Keys (OpenAI, ElevenLabs, D-ID)

### Step 1: Configure Environment

```bash
cd Backend
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
OPENAI_API_KEY=your-key
ELEVENLABS_API_KEY=your-key
DID_API_KEY=your-key
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
JWT_SECRET=your-random-secret

# MongoDB (default values work fine)
MONGO_USERNAME=admin
MONGO_PASSWORD=admin123
```

### Step 2: Start Everything

```bash
cd Backend
docker-compose up --build
```

This starts:
- ✅ MongoDB on port 27017
- ✅ Backend API on port 5000
- ✅ Frontend on port 3000

### Step 3: Access the App

Open browser: **http://localhost:3000**

## What's Running?

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | React app |
| Backend API | 5000 | Flask server |
| MongoDB | 27017 | Database |

## Verify MongoDB

```bash
# Check MongoDB is running
docker ps | grep mongodb

# Connect to MongoDB
docker exec -it eduvideo-mongodb mongosh -u admin -p admin123

# View data
use eduvideo
show collections
db.users.countDocuments()
db.chats.countDocuments()
```

## Features

### User Authentication
- ✅ Google OAuth login
- ✅ JWT tokens
- ✅ Protected routes
- ✅ User profiles in MongoDB

### Chat Dashboard
- ✅ Create multiple chats
- ✅ Switch between chats
- ✅ Rename chats
- ✅ Delete chats
- ✅ Chat history persists!

### Video Generation
- ✅ Generate educational videos
- ✅ AI-powered content
- ✅ Timeline progress tracking
- ✅ Download videos

## File Structure

```
Backend/
├── database.py          # MongoDB connection
├── models.py            # Data models
├── auth.py              # Authentication
├── chat_manager.py      # Chat operations
├── api_server.py        # API endpoints
├── docker-compose.yml   # Services config
└── .env                 # Your config

Client/
├── src/
│   ├── components/
│   │   └── dashboard/
│   │       └── Sidebar.tsx     # Chat list
│   ├── context/
│   │   ├── authContext.tsx     # Auth state
│   │   └── chatContext.tsx     # Chat state
│   └── pages/
│       ├── Landing.tsx         # Home page
│       ├── Login.tsx           # Login page
│       └── chatInterface.tsx   # Main app
└── Dockerfile
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v
```

## Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker logs ai-video-generator
docker logs eduvideo-mongodb
docker logs video-generator-client
```

## Troubleshooting

### MongoDB not starting
```bash
docker logs eduvideo-mongodb
# Check port 27017 is available
```

### Backend connection error
```bash
docker logs ai-video-generator | grep -i mongo
# Should see "MongoDB connected successfully"
```

### Frontend not loading
```bash
docker logs video-generator-client
# Check nginx configuration
```

### Can't login
- Verify GOOGLE_CLIENT_ID in .env
- Check authorized redirect URIs in Google Console
- See SETUP_AUTH.md for details

## Development

### Local Backend (without Docker)

```bash
# Start MongoDB in Docker
docker run -d --name mongo -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  mongo:7.0

# Run backend
cd Backend
pip install -r requirements.txt
python api_server.py
```

### Local Frontend (without Docker)

```bash
cd Client
npm install
npm run dev
# Access at http://localhost:5173
```

## Database Management

### Backup Data

```bash
docker exec eduvideo-mongodb mongodump \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --db eduvideo \
  --out /dump

docker cp eduvideo-mongodb:/dump ./backup
```

### Restore Data

```bash
docker cp ./backup eduvideo-mongodb:/dump

docker exec eduvideo-mongodb mongorestore \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --db eduvideo \
  /dump/eduvideo
```

### View Data with MongoDB Compass

1. Download: https://www.mongodb.com/products/compass
2. Connect: `mongodb://admin:admin123@localhost:27017`
3. Browse: `eduvideo` database

## API Endpoints

### Authentication
- POST `/api/auth/google` - Login with Google
- GET `/api/auth/me` - Get current user
- GET `/api/auth/verify` - Verify JWT token

### Chats
- GET `/api/chats` - List all chats
- POST `/api/chats` - Create new chat
- GET `/api/chats/{id}` - Get chat with messages
- PATCH `/api/chats/{id}` - Update chat title
- DELETE `/api/chats/{id}` - Delete chat

### Messages
- POST `/api/chats/{id}/messages` - Add message
- GET `/api/chats/{id}/messages` - Get messages
- POST `/api/chats/{id}/clear` - Clear messages

### Videos
- POST `/api/generate` - Generate video
- GET `/api/status/{job_id}` - Check status
- GET `/api/download/{job_id}` - Download video

## Documentation

- **MONGODB_SETUP.md** - MongoDB configuration & troubleshooting
- **MONGODB_MIGRATION.md** - Migration details
- **SETUP_AUTH.md** - Google OAuth setup
- **CHAT_DASHBOARD_FEATURE.md** - Chat features
- **IMPLEMENTATION_SUMMARY.md** - Complete overview

## Next Steps

1. ✅ Set up Google OAuth (see SETUP_AUTH.md)
2. ✅ Configure API keys
3. ✅ Start services with `docker-compose up`
4. ✅ Access at http://localhost:3000
5. ✅ Create your first video!

## Production Deployment

For production:
- Change MongoDB credentials
- Use strong JWT_SECRET
- Enable SSL/TLS
- Set up backups
- Configure monitoring
- Use environment-specific configs

See MONGODB_SETUP.md for production checklist.

## Support

Need help?
1. Check documentation files
2. Review logs: `docker-compose logs`
3. Verify MongoDB: `docker exec eduvideo-mongodb mongosh --eval "db.adminCommand('ping')"`
4. Check GitHub issues

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Backend**: Python, Flask, PyMongo
- **Database**: MongoDB 7.0
- **Auth**: Google OAuth 2.0, JWT
- **AI**: OpenAI, ElevenLabs, D-ID
- **Video**: Manim
- **Deployment**: Docker, Docker Compose, Nginx

---

**Status**: ✅ Ready for Development
**Last Updated**: 2025-01-11
