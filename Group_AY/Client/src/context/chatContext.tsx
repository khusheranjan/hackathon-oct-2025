import React, { createContext, useContext, useState } from "react";
import { useAuth } from "./authContext";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface Chat {
  id: string;
  title: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

interface ChatContextType {
  activeChat: Chat | null;
  activeChatId: string | null;
  isLoading: boolean;
  createNewChat: () => Promise<string | null>;
  loadChat: (chatId: string) => Promise<void>;
  addMessage: (message: { role: "user" | "assistant"; content: string }) => Promise<void>;
  clearMessages: () => Promise<void>;
  setActiveChatId: (chatId: string | null) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [activeChat, setActiveChat] = useState<Chat | null>(null);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { token } = useAuth();

  const API_BASE_URL = import.meta.env.VITE_URL || "";

  const createNewChat = async (): Promise<string | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: "New Chat" }),
      });

      if (response.ok) {
        const data = await response.json();
        setActiveChat(data.chat);
        setActiveChatId(data.chat.id);
        return data.chat.id;
      }
    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
    return null;
  };

  const loadChat = async (chatId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setActiveChat(data.chat);
        setActiveChatId(data.chat.id);
      }
    } catch (error) {
      console.error("Failed to load chat:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const addMessage = async (message: {
    role: "user" | "assistant";
    content: string;
  }) => {
    if (!activeChatId) {
      // Create new chat if none exists
      const newChatId = await createNewChat();
      if (!newChatId) return;
    }

    const chatId = activeChatId!;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chats/${chatId}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(message),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setActiveChat(data.chat);
      }
    } catch (error) {
      console.error("Failed to add message:", error);
    }
  };

  const clearMessages = async () => {
    if (!activeChatId) return;

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/chats/${activeChatId}/clear`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setActiveChat(data.chat);
      }
    } catch (error) {
      console.error("Failed to clear messages:", error);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        activeChat,
        activeChatId,
        isLoading,
        createNewChat,
        loadChat,
        addMessage,
        clearMessages,
        setActiveChatId,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
