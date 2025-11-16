"""
Chat session management for storing user conversations using MongoDB
"""

import uuid
from datetime import datetime
from typing import List, Optional
from database import get_chats_collection, get_messages_collection
from models import Chat, Message, str_to_objectid
from bson import ObjectId


def create_chat_session(user_id: str, title: str = "New Chat") -> dict:
    """
    Create a new chat session for a user in MongoDB
    """
    chats_collection = get_chats_collection()

    new_chat = Chat.create(user_id=user_id, title=title)
    result = chats_collection.insert_one(new_chat)

    new_chat['_id'] = result.inserted_id
    chat_dict = Chat.to_dict(new_chat, include_messages=True)
    chat_dict['messages'] = []  # New chat has no messages

    return chat_dict


def get_chat_session(chat_id: str, user_id: str) -> Optional[dict]:
    """
    Get a specific chat session with all messages (verify ownership)
    """
    chats_collection = get_chats_collection()
    messages_collection = get_messages_collection()

    # Convert string ID to ObjectId
    chat_object_id = str_to_objectid(chat_id)
    if not chat_object_id:
        return None

    # Get chat
    chat_doc = chats_collection.find_one({"_id": chat_object_id})

    if not chat_doc or chat_doc['user_id'] != user_id:
        return None

    # Get messages for this chat
    messages_cursor = messages_collection.find({"chat_id": chat_id}).sort("timestamp", 1)
    messages = [Message.to_dict(msg) for msg in messages_cursor]

    # Convert chat to dict
    chat_dict = Chat.to_dict(chat_doc, include_messages=True)
    chat_dict['messages'] = messages

    return chat_dict


def get_user_chats(user_id: str, limit: int = 50, offset: int = 0) -> List[dict]:
    """
    Get all chat sessions for a user (paginated)
    """
    chats_collection = get_chats_collection()

    # Find all chats for user, sorted by updated_at descending
    chats_cursor = chats_collection.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).skip(offset).limit(limit)

    chats = [Chat.to_summary(chat_doc) for chat_doc in chats_cursor]

    return chats


def update_chat_title(chat_id: str, user_id: str, title: str) -> Optional[dict]:
    """
    Update chat session title
    """
    chats_collection = get_chats_collection()

    # Convert string ID to ObjectId
    chat_object_id = str_to_objectid(chat_id)
    if not chat_object_id:
        return None

    # Update chat
    result = chats_collection.update_one(
        {"_id": chat_object_id, "user_id": user_id},
        {
            "$set": {
                "title": title,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        return None

    # Return updated chat
    chat_doc = chats_collection.find_one({"_id": chat_object_id})
    return Chat.to_dict(chat_doc) if chat_doc else None


def delete_chat_session(chat_id: str, user_id: str) -> bool:
    """
    Delete a chat session and all its messages
    """
    chats_collection = get_chats_collection()
    messages_collection = get_messages_collection()

    # Convert string ID to ObjectId
    chat_object_id = str_to_objectid(chat_id)
    if not chat_object_id:
        return False

    # Verify ownership and delete chat
    result = chats_collection.delete_one({"_id": chat_object_id, "user_id": user_id})

    if result.deleted_count == 0:
        return False

    # Delete all messages for this chat
    messages_collection.delete_many({"chat_id": chat_id})

    return True


def add_message_to_chat(chat_id: str, user_id: str, message: dict) -> Optional[dict]:
    """
    Add a message to a chat session
    """
    chats_collection = get_chats_collection()
    messages_collection = get_messages_collection()

    # Convert string ID to ObjectId
    chat_object_id = str_to_objectid(chat_id)
    if not chat_object_id:
        return None

    # Verify chat exists and user owns it
    chat_doc = chats_collection.find_one({"_id": chat_object_id, "user_id": user_id})
    if not chat_doc:
        return None

    # Create and insert message
    new_message = Message.create(
        chat_id=chat_id,
        role=message['role'],
        content=message['content']
    )
    messages_collection.insert_one(new_message)

    # Update chat's updated_at and message count
    update_data = {
        "updated_at": datetime.utcnow(),
        "$inc": {"message_count": 1}
    }

    # Auto-generate title from first user message
    if chat_doc.get('message_count', 0) == 0 and message.get('role') == 'user':
        content = message.get('content', '')
        auto_title = content[:50] + ('...' if len(content) > 50 else '')
        update_data["title"] = auto_title

    chats_collection.update_one(
        {"_id": chat_object_id},
        {"$set": update_data}
    )

    # Return updated chat with messages
    return get_chat_session(chat_id, user_id)


def get_chat_messages(chat_id: str, user_id: str) -> Optional[List[dict]]:
    """
    Get all messages from a chat session
    """
    chats_collection = get_chats_collection()
    messages_collection = get_messages_collection()

    # Convert string ID to ObjectId
    chat_object_id = str_to_objectid(chat_id)
    if not chat_object_id:
        return None

    # Verify chat exists and user owns it
    chat_doc = chats_collection.find_one({"_id": chat_object_id, "user_id": user_id})
    if not chat_doc:
        return None

    # Get all messages
    messages_cursor = messages_collection.find({"chat_id": chat_id}).sort("timestamp", 1)
    messages = [Message.to_dict(msg) for msg in messages_cursor]

    return messages


def clear_chat_messages(chat_id: str, user_id: str) -> Optional[dict]:
    """
    Clear all messages from a chat session
    """
    chats_collection = get_chats_collection()
    messages_collection = get_messages_collection()

    # Convert string ID to ObjectId
    chat_object_id = str_to_objectid(chat_id)
    if not chat_object_id:
        return None

    # Verify chat exists and user owns it
    chat_doc = chats_collection.find_one({"_id": chat_object_id, "user_id": user_id})
    if not chat_doc:
        return None

    # Delete all messages for this chat
    messages_collection.delete_many({"chat_id": chat_id})

    # Update chat's message count and updated_at
    chats_collection.update_one(
        {"_id": chat_object_id},
        {
            "$set": {
                "message_count": 0,
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Return updated chat
    return get_chat_session(chat_id, user_id)
