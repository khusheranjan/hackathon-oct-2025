  # Chat Dashboard Feature

A Claude-like dashboard interface for managing multiple chat sessions with persistent storage.

## Features

### Backend (Flask)

1. **Chat Session Management** (`Backend/chat_manager.py`)
   - Create new chat sessions
   - List all user chats
   - Get specific chat with messages
   - Update chat titles
   - Delete chat sessions
   - Add messages to chats
   - Clear chat messages
   - Auto-generate titles from first message

2. **API Endpoints** (`Backend/api_server.py`)
   - `GET /api/chats` - List all user chats (paginated)
   - `POST /api/chats` - Create new chat
   - `GET /api/chats/<chat_id>` - Get specific chat with messages
   - `PATCH /api/chats/<chat_id>` - Update chat title
   - `DELETE /api/chats/<chat_id>` - Delete chat
   - `POST /api/chats/<chat_id>/messages` - Add message
   - `GET /api/chats/<chat_id>/messages` - Get messages
   - `POST /api/chats/<chat_id>/clear` - Clear all messages

3. **Authentication**
   - All chat endpoints are protected with `@require_auth` decorator
   - JWT token required in Authorization header
   - Chats are user-specific (verified by user_id)

### Frontend (React)

1. **Sidebar Component** (`Client/src/components/dashboard/Sidebar.tsx`)
   - Lists all user chats
   - Create new chat button
   - Click to switch between chats
   - Rename chat (inline editing)
   - Delete chat with confirmation
   - Shows last updated time (Today, Yesterday, This Week, etc.)
   - Active chat highlighting

2. **Chat Context** (`Client/src/context/chatContext.tsx`)
   - Manages active chat state
   - Creates new chats
   - Loads chat messages
   - Adds messages to backend
   - Clears chat messages
   - Syncs with backend API

3. **Updated Components**
   - **ChatInterface**: Now includes sidebar and manages chat switching
   - **Header**: Added sidebar toggle button (hamburger menu)
   - **ChatContainer**:
     - Loads messages from active chat
     - Saves user and assistant messages to backend
     - Maintains video generation functionality

## Data Flow

### Creating a New Chat

```
User clicks "New Chat"
  → ChatContext.createNewChat()
  → POST /api/chats
  → Backend creates chat session
  → Returns chat with ID
  → Frontend sets as active chat
  → ChatContainer clears and ready for new messages
```

### Sending a Message

```
User types message and sends
  → ChatContainer.sendPrompt()
  → Adds message to local state (instant UI update)
  → ChatContext.addMessage() (saves to backend)
  → POST /api/chats/<chat_id>/messages
  → Backend saves message
  → Video generation proceeds as normal
  → When complete, assistant message saved to backend
```

### Switching Chats

```
User clicks chat in sidebar
  → ChatContext.loadChat(chatId)
  → GET /api/chats/<chat_id>
  → Backend returns chat with all messages
  → ChatContainer loads messages from context
  → UI displays chat history
```

### Deleting a Chat

```
User clicks delete icon
  → Confirmation dialog
  → Sidebar.handleDeleteChat()
  → DELETE /api/chats/<chat_id>
  → Backend deletes chat
  → Sidebar removes from list
  → If active chat, creates new chat
```

## Storage

Currently using **in-memory storage** in Python dictionaries:
- `chat_sessions`: Dict[chat_id, chat_data]
- `user_chats`: Dict[user_id, [chat_ids]]

### Migration to Database

To migrate to a database (PostgreSQL, MongoDB, etc.):

1. Replace `chat_manager.py` functions with database queries
2. Keep the same function signatures and return types
3. No frontend changes needed
4. Add database models/schemas:
   - `Chat` model: id, user_id, title, created_at, updated_at
   - `Message` model: id, chat_id, role, content, timestamp

Example schema (SQL):

```sql
CREATE TABLE chats (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_chat_id (chat_id)
);
```

## UI/UX Features

### Sidebar
- **Width**: 256px (w-64)
- **Position**: Fixed left side
- **Toggle**: Hamburger menu in header
- **Scroll**: Independent scrolling for chat list
- **Hover Effects**: Edit and delete buttons appear on hover
- **Active State**: Highlighted with accent color

### Chat List Item
- **Icon**: Message square icon
- **Title**: Chat title (truncated if too long)
- **Date**: Relative time (Today, Yesterday, etc.)
- **Actions**:
  - Edit (pencil icon) - inline editing with save/cancel
  - Delete (trash icon) - confirmation required
- **Editing**: Click edit → inline input → Enter to save, Esc to cancel

### Header
- **Hamburger Menu**: Toggle sidebar visibility
- **Clear Chat**: Clears current chat messages
- **Theme Toggle**: Light/Dark mode
- **User Info**: Profile picture and name
- **Logout**: Sign out button

## Keyboard Shortcuts

- **Enter**: Save chat title when editing
- **Escape**: Cancel chat title editing
- **Click outside**: Cancel editing (if implemented)

## Error Handling

- Failed to load chats: Shows error message
- Failed to create chat: Silent fail, tries again
- Failed to delete: Shows error in console
- Failed to save message: Message still shows in UI (optimistic update)
- Network errors: Graceful degradation

## Performance Considerations

1. **Pagination**: Backend supports limit/offset for large chat lists
2. **Lazy Loading**: Only loads messages when chat is selected
3. **Optimistic Updates**: UI updates immediately, syncs with backend
4. **Debouncing**: Title edits could be debounced (not implemented yet)
5. **Caching**: Chat list cached in Sidebar state

## Security

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: Users can only access their own chats
3. **Validation**: Input validation on backend (title length, required fields)
4. **XSS Protection**: React escapes content by default
5. **CSRF**: Using JWT tokens (not cookies)

## Future Enhancements

1. **Search**: Search through chat titles and messages
2. **Folders**: Organize chats into folders/categories
3. **Export**: Export chat history as JSON/PDF
4. **Share**: Share chat with others (read-only link)
5. **Archive**: Archive old chats instead of deleting
6. **Favorites**: Star/favorite important chats
7. **Tags**: Add tags to chats for organization
8. **Keyboard Navigation**: Arrow keys to navigate chat list
9. **Drag & Drop**: Reorder chats manually
10. **Bulk Actions**: Select multiple chats for deletion

## Testing

To test the feature:

1. **Create Chat**: Click "New Chat" button
2. **Send Message**: Type and send a message
3. **Switch Chats**: Click another chat in sidebar
4. **Verify Persistence**: Refresh page, chats should persist
5. **Edit Title**: Click edit icon, change title, press Enter
6. **Delete Chat**: Click delete icon, confirm deletion
7. **Toggle Sidebar**: Click hamburger menu to hide/show

## Troubleshooting

### Chat list not loading
- Check JWT token is valid
- Check backend is running
- Check browser console for errors
- Verify `/api/chats` endpoint returns data

### Messages not saving
- Check active chat ID exists
- Check backend receives POST requests
- Verify user is authenticated
- Check network tab for failed requests

### Sidebar not appearing
- Check `isSidebarOpen` state
- Verify Sidebar component is rendered
- Check CSS classes for visibility

### Chat not switching
- Verify `loadChat` function is called
- Check `activeChat?.id` in useEffect dependency
- Confirm backend returns chat data
- Check ChatContainer receives new messages

## Related Files

### Backend
- `Backend/chat_manager.py` - Chat session management
- `Backend/api_server.py` - API endpoints
- `Backend/auth.py` - Authentication decorators

### Frontend
- `Client/src/components/dashboard/Sidebar.tsx` - Sidebar component
- `Client/src/context/chatContext.tsx` - Chat state management
- `Client/src/pages/chatInterface.tsx` - Main chat interface
- `Client/src/components/home/chatContainer.tsx` - Chat messages
- `Client/src/components/home/header.tsx` - Header with toggle
