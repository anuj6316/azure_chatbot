import React from "react";
import type { Message as MessageType } from "../types";
import { BotIcon, UserIcon } from "./icons";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MessageProps {
  message: MessageType;
  isLoading?: boolean;
}

const PulsingLoader: React.FC = () => (
  <div className="flex items-center space-x-2">
    <div
      className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-pulse"
      style={{ animationDelay: "0s" }}
    ></div>
    <div
      className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-pulse"
      style={{ animationDelay: "0.2s" }}
    ></div>
    <div
      className="w-2 h-2 bg-gray-500 dark:bg-gray-400 rounded-full animate-pulse"
      style={{ animationDelay: "0.4s" }}
    ></div>
  </div>
);

const Message: React.FC<MessageProps> = ({ message, isLoading = false }) => {
  const isUser = message.sender === "user";
  const isBot = message.sender === "bot";
  const isError = message.sender === "error";

  if (isError) {
    return (
      <div className="flex justify-center my-2">
        <p className="text-red-500 dark:text-red-400 bg-red-500/10 px-4 py-2 rounded-lg text-sm">
          {message.text}
        </p>
      </div>
    );
  }

  return (
    <div
      className={`flex items-end gap-3 ${isUser ? "justify-end" : "justify-start"}`}
    >
      {isBot && (
        <div className="w-8 h-8 flex-shrink-0 rounded-full">
          <BotIcon className="w-8 h-8 text-blue-500" />
        </div>
      )}

      <div
        className={`max-w-md lg:max-w-2xl px-4 py-3 rounded-2xl ${
          isUser
            ? "bg-blue-600 text-white rounded-br-none"
            : "bg-gray-100 dark:bg-[#2c2e42] text-gray-800 dark:text-gray-200 rounded-bl-none"
        }`}
      >
        {isLoading ? (
          <PulsingLoader />
        ) : (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            className="prose dark:prose-invert max-w-none"
            components={{
              p: ({ node, ...props }) => (
                <p className="leading-relaxed" {...props} />
              ),
            }}
          >
            {message.text}
          </ReactMarkdown>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 flex-shrink-0 rounded-full">
          <UserIcon className="w-8 h-8 text-gray-500 dark:text-gray-400" />
        </div>
      )}
    </div>
  );
};

export { Message };
