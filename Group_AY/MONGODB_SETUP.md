# MongoDB Setup Guide

This guide explains how MongoDB is configured and used in the EduVideo AI application.

## Overview

The application now uses **MongoDB** for persistent data storage instead of in-memory dictionaries. MongoDB runs in a Docker container alongside the application.

## Architecture

### Collections

The database (`eduvideo`) contains three collections:

1. **users** - User accounts from Google OAuth
2. **chats** - Chat sessions
3. **messages** - Individual messages within chats

### Data Models

#### Users Collection
```javascript
{
  _id: ObjectId,
  google_id: String (unique),    // Google OAuth user ID
  email: String,
  name: String,
  picture: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `google_id` (unique)
- `email`

#### Chats Collection
```javascript
{
  _id: ObjectId,
  user_id: String,               // Google ID of owner
  title: String,
  message_count: Number,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `user_id`
- `updated_at` (descending)
- Compound: `(user_id, updated_at)` (descending)

#### Messages Collection
```javascript
{
  _id: ObjectId,
  chat_id: String,               // String ID of chat
  role: String,                  // "user" or "assistant"
  content: String,
  timestamp: DateTime
}
```

**Indexes:**
- `chat_id`
- Compound: `(chat_id, timestamp)` (ascending)

## Docker Configuration

### docker-compose.yml

MongoDB is configured in `docker-compose.yml`:

```yaml
mongodb:
  image: mongo:7.0
  container_name: eduvideo-mongodb
  ports:
    - "27017:27017"
  environment:
    - MONGO_INITDB_ROOT_USERNAME=${MONGO_USERNAME:-admin}
    - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD:-admin123}
    - MONGO_INITDB_DATABASE=eduvideo
  volumes:
    - mongodb_data:/data/db
    - mongodb_config:/data/configdb
  healthcheck:
    test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
    interval: 10s
    timeout: 5s
    retries: 5
```

### Volumes

Two persistent volumes are created:
- `mongodb_data` - Database files
- `mongodb_config` - Configuration files

Data persists across container restarts!

## Environment Variables

### Docker (Automatic)

When using Docker Compose, MongoDB URI is auto-configured:

```bash
MONGODB_URI=mongodb://admin:admin123@mongodb:27017/eduvideo?authSource=admin
```

### Local Development

For running backend locally (without Docker):

```bash
# .env file
MONGO_USERNAME=admin
MONGO_PASSWORD=admin123
MONGODB_URI=mongodb://admin:admin123@localhost:27017/eduvideo?authSource=admin
```

## Backend Implementation

### File Structure

```
Backend/
├── database.py          # MongoDB connection & initialization
├── models.py            # Data models (User, Chat, Message)
├── auth.py              # User authentication (MongoDB)
├── chat_manager.py      # Chat operations (MongoDB)
└── api_server.py        # API endpoints
```

### Key Functions

#### database.py
- `connect_to_mongodb()` - Establish connection
- `initialize_collections()` - Create indexes
- `get_collection(name)` - Get collection reference
- `close_connection()` - Cleanup on shutdown

#### models.py
- `User.create()` / `User.to_dict()` - User model
- `Chat.create()` / `Chat.to_dict()` - Chat model
- `Message.create()` / `Message.to_dict()` - Message model
- `str_to_objectid()` - Convert string IDs

#### chat_manager.py (Updated)
All functions now use MongoDB:
- `create_chat_session()` - Creates in DB
- `get_chat_session()` - Loads from DB with messages
- `get_user_chats()` - Queries with pagination
- `add_message_to_chat()` - Inserts message
- `delete_chat_session()` - Deletes chat + messages

## Running the Application

### With Docker (Recommended)

```bash
cd Backend
docker-compose up --build
```

This will:
1. Start MongoDB container
2. Wait for MongoDB to be healthy
3. Start backend (connects to MongoDB)
4. Start frontend

### Local Development

**1. Start MongoDB:**
```bash
docker run -d \
  --name eduvideo-mongo \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=admin123 \
  mongo:7.0
```

**2. Run Backend:**
```bash
cd Backend
pip install -r requirements.txt
python api_server.py
```

**3. Run Frontend:**
```bash
cd Client
npm run dev
```

## Accessing MongoDB

### Using MongoDB Compass

1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect with URI: `mongodb://admin:admin123@localhost:27017`
3. Browse collections in `eduvideo` database

### Using mongosh (CLI)

```bash
# Connect to container
docker exec -it eduvideo-mongodb mongosh -u admin -p admin123

# Use database
use eduvideo

# List collections
show collections

# Query examples
db.users.find()
db.chats.find({user_id: "google_user_id"})
db.messages.find({chat_id: "chat_id"}).sort({timestamp: 1})

# Count documents
db.chats.countDocuments()
db.messages.countDocuments()
```

## Data Migration

### Exporting Data

```bash
# Export entire database
docker exec eduvideo-mongodb mongodump \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --db eduvideo \
  --out /dump

# Copy from container
docker cp eduvideo-mongodb:/dump ./mongodb_backup
```

### Importing Data

```bash
# Copy to container
docker cp ./mongodb_backup eduvideo-mongodb:/dump

# Import
docker exec eduvideo-mongodb mongorestore \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --db eduvideo \
  /dump/eduvideo
```

## Backup Strategy

### Automated Backups (Production)

Add this to docker-compose.yml:

```yaml
mongodb-backup:
  image: tiredofit/mongodb-backup
  depends_on:
    - mongodb
  environment:
    - MONGO_HOST=mongodb
    - MONGO_PORT=27017
    - MONGO_USER=admin
    - MONGO_PASS=admin123
    - BACKUP_INTERVAL=daily
    - BACKUP_TIME=0200
  volumes:
    - ./backups:/backup
```

### Manual Backup Script

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker exec eduvideo-mongodb mongodump \
  --username admin \
  --password admin123 \
  --authenticationDatabase admin \
  --db eduvideo \
  --gzip \
  --archive=/backup/eduvideo_$DATE.gz
```

## Performance Optimization

### Indexes

All indexes are created automatically on startup in `database.py`:

```python
# Users
users.create_index([("google_id", ASCENDING)], unique=True)
users.create_index([("email", ASCENDING)])

# Chats
chats.create_index([("user_id", ASCENDING)])
chats.create_index([("updated_at", DESCENDING)])
chats.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])

# Messages
messages.create_index([("chat_id", ASCENDING)])
messages.create_index([("chat_id", ASCENDING), ("timestamp", ASCENDING)])
```

### Query Optimization

- Chat list query uses compound index for efficiency
- Messages are queried with chat_id index
- Pagination is implemented with skip/limit

### Connection Pooling

PyMongo automatically manages connection pooling. Default settings:
- Max pool size: 100 connections
- Min pool size: 0
- Server selection timeout: 5 seconds

## Troubleshooting

### MongoDB Container Won't Start

```bash
# Check logs
docker logs eduvideo-mongodb

# Common issues:
# 1. Port 27017 already in use
sudo lsof -i :27017
# Kill process or change port

# 2. Permission issues on volumes
sudo chown -R 999:999 mongodb_data mongodb_config
```

### Connection Timeout

```bash
# Check MongoDB is running
docker ps | grep mongodb

# Check connectivity
docker exec eduvideo-mongodb mongosh --eval "db.adminCommand('ping')"

# Check backend logs
docker logs ai-video-generator | grep -i mongo
```

### Data Not Persisting

```bash
# Check volumes exist
docker volume ls | grep mongodb

# Inspect volume
docker volume inspect mongodb_data

# Verify data directory
docker exec eduvideo-mongodb ls -la /data/db
```

### Slow Queries

```bash
# Enable profiling
docker exec -it eduvideo-mongodb mongosh -u admin -p admin123
use eduvideo
db.setProfilingLevel(2)

# View slow queries
db.system.profile.find({millis: {$gt: 100}}).sort({ts: -1}).limit(10)

# Analyze query plan
db.chats.find({user_id: "xxx"}).explain("executionStats")
```

## Security Considerations

### Production Checklist

- [ ] Change default MongoDB credentials
- [ ] Use strong passwords (20+ characters)
- [ ] Enable MongoDB authentication
- [ ] Restrict MongoDB port (remove from docker-compose ports)
- [ ] Use MongoDB SSL/TLS
- [ ] Enable MongoDB access control
- [ ] Regular security updates
- [ ] Implement backup strategy
- [ ] Monitor database logs

### Hardening MongoDB

```yaml
# docker-compose.yml (production)
mongodb:
  image: mongo:7.0
  # Don't expose port externally
  expose:
    - "27017"
  environment:
    - MONGO_INITDB_ROOT_USERNAME=${MONGO_USERNAME}
    - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
  command: mongod --auth --tlsMode requireTLS --tlsCertificateKeyFile /certs/mongodb.pem
  volumes:
    - ./certs:/certs:ro
```

## Monitoring

### Basic Monitoring

```bash
# Database stats
docker exec -it eduvideo-mongodb mongosh -u admin -p admin123 --eval "
  use eduvideo
  db.stats()
"

# Collection stats
docker exec -it eduvideo-mongodb mongosh -u admin -p admin123 --eval "
  use eduvideo
  db.chats.stats()
  db.messages.stats()
"

# Current operations
docker exec -it eduvideo-mongodb mongosh -u admin -p admin123 --eval "
  db.currentOp()
"
```

### Production Monitoring

Consider using:
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) - Managed MongoDB
- [Prometheus + Grafana](https://github.com/percona/mongodb_exporter)
- [MongoDB Cloud Manager](https://www.mongodb.com/cloud/cloud-manager)

## Migration from In-Memory

The migration is complete! All data now persists in MongoDB:

| Old (In-Memory) | New (MongoDB) |
|----------------|---------------|
| `users_db` dict | `users` collection |
| `chat_sessions` dict | `chats` collection |
| `user_chats` dict | Queried from `chats` |
| messages in dict | `messages` collection |

## Next Steps

1. **Set up monitoring** - Track database performance
2. **Implement backups** - Automated daily backups
3. **Add data validation** - MongoDB schema validation
4. **Optimize queries** - Analyze slow queries
5. **Scale MongoDB** - Replica sets for high availability

## Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)
- [MongoDB Docker Hub](https://hub.docker.com/_/mongo)
- [MongoDB University](https://university.mongodb.com/) - Free courses

## Support

If you encounter issues:
1. Check logs: `docker logs eduvideo-mongodb`
2. Verify connection: `docker exec eduvideo-mongodb mongosh --eval "db.adminCommand('ping')"`
3. Review indexes: `db.chats.getIndexes()`
4. Check this documentation for troubleshooting steps
