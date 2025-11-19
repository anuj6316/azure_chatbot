import React, { useState, useEffect } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatWindow } from "./components/ChatWindow";
import type { Message, ChatSession } from "./types";

const API_URL = "http://localhost:8000";
console.log("API_URL:", API_URL);

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  // Session Management
  const [sessions, setSessions] = useState<ChatSession[]>(() => {
    const stored = localStorage.getItem("chat_sessions");
    return stored ? JSON.parse(stored) : [];
  });

  const [sessionId, setSessionId] = useState<string>(() => {
    const stored = localStorage.getItem("current_session_id");
    if (stored) return stored;
    // If no session, create one immediately
    const newId = crypto.randomUUID();
    return newId;
  });

  // Persist sessions and current ID
  useEffect(() => {
    localStorage.setItem("chat_sessions", JSON.stringify(sessions));
  }, [sessions]);

  useEffect(() => {
    localStorage.setItem("current_session_id", sessionId);
  }, [sessionId]);

  // Ensure at least one session exists on load
  useEffect(() => {
    if (sessions.length === 0) {
      const initialSession: ChatSession = {
        id: sessionId,
        title: "New Chat",
        date: new Date().toISOString(),
      };
      setSessions([initialSession]);
    }
  }, []); // Run once

  // Fetch history when switching sessions
  useEffect(() => {
    const fetchHistory = async () => {
      if (!sessionId) return;
      setIsLoading(true);
      try {
        const res = await fetch(`${API_URL}/chat_history/${sessionId}`);
        if (res.ok) {
          const data = await res.json();
          setMessages(data.messages || []);
        } else {
          setMessages([]);
        }
      } catch (e) {
        console.error("Failed to load history", e);
        setMessages([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [sessionId]);


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

    // Update session title if it's the first message and title is "New Chat"
    setSessions(prev => prev.map(s => {
      if (s.id === sessionId && s.title === "New Chat") {
        return { ...s, title: userInput.slice(0, 30) + (userInput.length > 30 ? "..." : "") };
      }
      return s;
    }));

    try {
      const response = await fetch(`${API_URL}/chat_response`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
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
        diagram: data.diagram,
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
    const newId = crypto.randomUUID();
    const newSession: ChatSession = {
      id: newId,
      title: "New Chat",
      date: new Date().toISOString(),
    };
    setSessions(prev => [newSession, ...prev]);
    setSessionId(newId);
    setMessages([]);
  };

  const handleDeleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    if (id === sessionId) {
      if (newSessions.length > 0) {
        setSessionId(newSessions[0].id);
      } else {
        // If deleted last session, create a new one
        handleNewChat();
      }
    }
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
        sessions={sessions}
        currentSessionId={sessionId}
        onSelectSession={setSessionId}
        onDeleteSession={handleDeleteSession}
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
