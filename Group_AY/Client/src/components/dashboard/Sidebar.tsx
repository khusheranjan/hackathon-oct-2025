import { useState, useEffect } from "react";
import { Plus, MessageSquare, Trash2, Edit2, Check, X } from "lucide-react";
import { Button } from "../ui/button";
import { useAuth } from "../../context/authContext";

interface Chat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface SidebarProps {
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
}

export default function Sidebar({
  activeChatId,
  onSelectChat,
  onNewChat,
}: SidebarProps) {
  const [chats, setChats] = useState<Chat[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const { token } = useAuth();

  const API_BASE_URL = import.meta.env.VITE_URL || "";

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setChats(data.chats);
      }
    } catch (error) {
      console.error("Failed to load chats:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteChat = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();

    if (!confirm("Are you sure you want to delete this chat?")) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setChats(chats.filter((chat) => chat.id !== chatId));
        if (activeChatId === chatId) {
          onNewChat();
        }
      }
    } catch (error) {
      console.error("Failed to delete chat:", error);
    }
  };

  const handleStartEdit = (chat: Chat, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(chat.id);
    setEditTitle(chat.title);
  };

  const handleSaveEdit = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();

    if (!editTitle.trim()) {
      setEditingId(null);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: editTitle }),
      });

      if (response.ok) {
        const data = await response.json();
        setChats(
          chats.map((chat) =>
            chat.id === chatId ? { ...chat, title: data.chat.title } : chat
          )
        );
      }
    } catch (error) {
      console.error("Failed to update chat:", error);
    } finally {
      setEditingId(null);
    }
  };

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return "Today";
    } else if (diffInHours < 48) {
      return "Yesterday";
    } else if (diffInHours < 168) {
      return "This Week";
    } else {
      return date.toLocaleDateString();
    }
  };

  // Refresh chats when a new chat is created
  useEffect(() => {
    if (activeChatId && !chats.find((c) => c.id === activeChatId)) {
      loadChats();
    }
  }, [activeChatId]);

  return (
    <aside className="w-64 border-r border-border bg-background flex flex-col h-screen">
      {/* Header */}
      <div className="p-4 border-b border-border">
        <Button onClick={onNewChat} className="w-full">
          <Plus className="w-4 h-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-muted-foreground text-sm">
            Loading chats...
          </div>
        ) : chats.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground text-sm">
            No chats yet. Start a new conversation!
          </div>
        ) : (
          <div className="py-2">
            {chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => onSelectChat(chat.id)}
                className={`group px-3 py-2 mx-2 rounded-lg cursor-pointer transition-colors ${
                  activeChatId === chat.id
                    ? "bg-accent"
                    : "hover:bg-accent/50"
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2 flex-1 min-w-0">
                    <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      {editingId === chat.id ? (
                        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                          <input
                            type="text"
                            value={editTitle}
                            onChange={(e) => setEditTitle(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                handleSaveEdit(chat.id, e as any);
                              } else if (e.key === "Escape") {
                                handleCancelEdit(e as any);
                              }
                            }}
                            className="flex-1 px-1 py-0.5 text-sm bg-background border border-border rounded"
                            autoFocus
                          />
                          <button
                            onClick={(e) => handleSaveEdit(chat.id, e)}
                            className="p-0.5 hover:bg-background rounded"
                          >
                            <Check className="w-3 h-3" />
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="p-0.5 hover:bg-background rounded"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ) : (
                        <>
                          <div className="text-sm font-medium truncate">
                            {chat.title}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {formatDate(chat.updated_at)}
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {editingId !== chat.id && (
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => handleStartEdit(chat, e)}
                        className="p-1 hover:bg-background rounded"
                        title="Rename"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                      <button
                        onClick={(e) => handleDeleteChat(chat.id, e)}
                        className="p-1 hover:bg-background rounded text-destructive"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
