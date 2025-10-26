import { useRef } from "react";
import ChatContainer from "../components/home/chatContainer";
import type { ChatContainerHandle } from "../components/home/chatContainer";
import Header from "../components/home/header";

export default function ChatInterface() {
  // ref to call imperative methods on ChatContainer
  const chatRef = useRef<ChatContainerHandle | null>(null);

  const handleClearChat = () => {
    chatRef.current?.clearMessages();
  };

  return (
    // page container: full viewport height and column layout
    <div className="min-h-screen flex flex-col bg-background">
      {/* pass the clear handler into header */}
      <Header onClearChat={handleClearChat} />

      {/* main area grows to fill remaining viewport height */}
      <main className="flex-1 w-full">
        <div className="max-w-4xl mx-auto h-full">
          {/* attach ref so parent can call clearMessages() */}
          <ChatContainer ref={chatRef} />
        </div>
      </main>
    </div>
  );
}
