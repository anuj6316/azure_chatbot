import React, { useState, useEffect } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatWindow } from "./components/ChatWindow";
import type { Message } from "./types";

const API_URL = "http://localhost:8000";

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  // ✅ Restore sessionId state (but keep the bugfix - no reset on refresh)
  const [sessionId, setSessionId] = useState<string>(() => {
    let storedSessionId = sessionStorage.getItem("chat_session_id");
    if (!storedSessionId) {
      storedSessionId = crypto.randomUUID();
      sessionStorage.setItem("chat_session_id", storedSessionId);
    }
    return storedSessionId;
  });

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const handleSendMessage = async (userInput: string) => {
    if (!userInput.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: userInput,
      sender: "user",
    };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat_response`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // ✅ Fixed: Added sessionId value here
        body: JSON.stringify({ query: userInput, session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.answer || "Sorry, I couldn't get a response.",
        sender: "bot",
      };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error("Failed to fetch chat response:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, something went wrong. Please try again later.",
        sender: "error",
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    // ✅ Optional: Generate new session for new chat
    const newSessionId = crypto.randomUUID();
    setSessionId(newSessionId);
    sessionStorage.setItem("chat_session_id", newSessionId);
  };

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "dark" ? "light" : "dark"));
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden antialiased bg-white dark:bg-[#171821]">
      <Sidebar
        onNewChat={handleNewChat}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  );
};

export { App };
