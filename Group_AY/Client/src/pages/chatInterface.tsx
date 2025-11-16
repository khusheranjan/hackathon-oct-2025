import { useRef, useState, useEffect } from "react";
import ChatContainer from "../components/home/chatContainer";
import type { ChatContainerHandle } from "../components/home/chatContainer";
import Header from "../components/home/header";
import Sidebar from "../components/dashboard/Sidebar";
import { useChat } from "../context/chatContext";

export default function ChatInterface() {
  const chatRef = useRef<ChatContainerHandle | null>(null);
  const { activeChatId, createNewChat, loadChat, clearMessages } = useChat();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Create initial chat on mount if none exists
  useEffect(() => {
    if (!activeChatId) {
      createNewChat();
    }
  }, []);

  const handleClearChat = async () => {
    await clearMessages();
    chatRef.current?.clearMessages();
  };

  const handleNewChat = async () => {
    await createNewChat();
    chatRef.current?.clearMessages();
  };

  const handleSelectChat = async (chatId: string) => {
    await loadChat(chatId);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      {isSidebarOpen && (
        <Sidebar
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
        />
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          onClearChat={handleClearChat}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        />

        <main className="flex-1 overflow-hidden">
          <div className="max-w-4xl mx-auto h-full">
            <ChatContainer ref={chatRef} />
          </div>
        </main>
      </div>
    </div>
  );
}
