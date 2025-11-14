import React, { useEffect, useRef } from "react";
import type { Message as MessageType } from "../types";
import { Message } from "./Message";
import { ChatInput } from "./ChatInput";
import {
  BotIcon,
  CheckIcon,
  LightbulbIcon,
  WarningIcon,
  ZapIcon,
} from "./icons";

interface ChatWindowProps {
  messages: MessageType[];
  isLoading: boolean;
  onSendMessage: (input: string) => void;
}

const WelcomeScreen: React.FC<{ onPromptClick: (prompt: string) => void }> = ({
  onPromptClick,
}) => {
  const examples = [
    "Explain quantum computing in simple terms",
    "Got any creative ideas for a 10 year old’s birthday?",
    "How do I make an HTTP request in Javascript?",
  ];
  const capabilities = [
    "Remembers what user said earlier in the conversation",
    "Allows user to provide follow-up corrections",
    "Trained to decline inappropriate requests",
  ];
  const limitations = [
    "May occasionally generate incorrect information",
    "May occasionally produce harmful instructions or biased content",
    "Limited knowledge of world and events after 2021",
  ];

  return (
    <div className="flex-1 flex flex-col justify-center items-center text-center p-4">
      <div className="relative w-20 h-20 mb-6">
        <div className="absolute inset-0 bg-blue-500 rounded-full blur-lg opacity-50"></div>
        <div className="relative bg-gray-200 dark:bg-[#202231] border border-gray-300 dark:border-white/10 rounded-full p-4">
          <BotIcon className="w-12 h-12 text-blue-500" />
        </div>
      </div>
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-10">
        How can I help you today?
      </h1>

      <div className="w-full max-w-4xl">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full mb-12">
          {examples.map((prompt, index) => (
            <button
              key={index}
              onClick={() => onPromptClick(prompt)}
              className="bg-gray-50 dark:bg-[#202231] border border-gray-300 dark:border-white/10 p-3.5 rounded-lg text-sm text-gray-700 dark:text-gray-300 text-center cursor-pointer hover:bg-gray-100 dark:hover:bg-[#2c2e42] transition-colors duration-200"
            >
              <p className="font-semibold mb-1">
                "{prompt.split(" ").slice(0, 3).join(" ")}..."
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Get a quick answer
              </p>
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
          <div>
            <div className="flex items-center justify-center mb-4">
              <ZapIcon className="w-6 h-6 text-gray-800 dark:text-white mr-2" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Capabilities
              </h2>
            </div>
            <ul className="space-y-3">
              {capabilities.map((item, index) => (
                <li
                  key={index}
                  className="flex items-start text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-[#202231] p-3 rounded-lg"
                >
                  <CheckIcon className="w-4 h-4 mr-3 mt-0.5 flex-shrink-0 text-green-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="flex items-center justify-center mb-4">
              <WarningIcon className="w-6 h-6 text-gray-800 dark:text-white mr-2" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Limitations
              </h2>
            </div>
            <ul className="space-y-3">
              {limitations.map((item, index) => (
                <li
                  key={index}
                  className="flex items-start text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-[#202231] p-3 rounded-lg"
                >
                  <WarningIcon className="w-4 h-4 mr-3 mt-0.5 flex-shrink-0 text-amber-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  isLoading,
  onSendMessage,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 flex flex-col no-scrollbar relative text-gray-800 dark:text-gray-200">
      <div className="flex-1 overflow-y-auto no-scrollbar p-4 md:p-6 space-y-4 pb-32 max-h-[90vh]">
        {messages.length === 0 ? (
          <WelcomeScreen onPromptClick={onSendMessage} />
        ) : (
          messages.map((msg) => <Message key={msg.id} message={msg} />)
        )}
        {isLoading && (
          <Message
            message={{ id: "loading", text: "...", sender: "bot" }}
            isLoading={true}
          />
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-white dark:from-[#171821] via-white/80 dark:via-[#171821]/80 to-transparent pt-8">
        <div className="mx-auto max-w-3xl px-4">
          <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
          <p className="text-xs text-center text-gray-400 dark:text-gray-500 py-3">
            Chatbot can make mistakes. Consider checking important information.
          </p>
        </div>
      </div>
    </div>
  );
};

export { ChatWindow };
