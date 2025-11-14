import React from 'react';
import { PlusIcon, ChatIcon, TrashIcon, UpgradeIcon, SunIcon, FaqIcon, LogoutIcon, MenuIcon, MoonIcon } from './icons';

interface SidebarProps {
  onNewChat: () => void;
  isOpen: boolean;
  onToggle: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewChat, isOpen, onToggle, theme, onToggleTheme }) => {
  return (
    <div className={`hidden md:flex flex-col bg-gray-100 dark:bg-[#202231] p-3 transition-all duration-300 ease-in-out ${isOpen ? 'w-64' : 'w-20'}`}>
       <div className={`flex items-center ${isOpen ? 'justify-between' : 'justify-center'} pb-2 mb-2 border-b border-gray-300 dark:border-white/10`}>
         {isOpen && <span className="text-lg font-semibold text-gray-800 dark:text-white">AI Chatbot</span>}
         <button onClick={onToggle} className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-[#2c2e42] text-gray-700 dark:text-gray-300 transition-colors">
            <MenuIcon className="w-6 h-6"/>
         </button>
      </div>

      <div
        onClick={onNewChat}
        className="flex items-center justify-center p-3 rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors cursor-pointer mb-4"
      >
        <PlusIcon className={`w-5 h-5 flex-shrink-0 ${isOpen && 'mr-2'}`} />
        {isOpen && <span>New chat</span>}
      </div>

      <div className="flex-1 overflow-y-auto pr-1 space-y-1">
        {/* Dummy Chat History */}
        <div className={`flex items-center p-3 rounded-lg text-sm text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-[#2c2e42] cursor-pointer ${!isOpen && 'justify-center'}`}>
          <ChatIcon className={`w-5 h-5 flex-shrink-0 ${isOpen && 'mr-3'}`} />
          {isOpen && <span>React State Management</span>}
        </div>
        <div className={`flex items-center p-3 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#2c2e42] cursor-pointer transition-colors ${!isOpen && 'justify-center'}`}>
          <ChatIcon className={`w-5 h-5 flex-shrink-0 ${isOpen && 'mr-3'}`} />
          {isOpen && <span>Tailwind CSS Tips</span>}
        </div>
      </div>

      <div className="border-t border-gray-300 dark:border-white/10 pt-3 space-y-1">
        <SidebarLink Icon={TrashIcon} text="Clear conversations" isOpen={isOpen} onClick={onNewChat} />
        <SidebarLink Icon={UpgradeIcon} text="Upgrade to Plus" isOpen={isOpen} />
        <SidebarLink 
          Icon={theme === 'dark' ? SunIcon : MoonIcon} 
          text={theme === 'dark' ? 'Light mode' : 'Dark mode'} 
          isOpen={isOpen}
          onClick={onToggleTheme}
        />
        <SidebarLink Icon={FaqIcon} text="Updates & FAQ" isOpen={isOpen} />
        <SidebarLink Icon={LogoutIcon} text="Log out" isOpen={isOpen} />
      </div>
    </div>
  );
};

interface SidebarLinkProps {
  Icon: React.ElementType;
  text: string;
  isOpen: boolean;
  onClick?: () => void;
}

const SidebarLink: React.FC<SidebarLinkProps> = ({ Icon, text, isOpen, onClick }) => {
  return (
    <div 
      onClick={onClick}
      className={`flex items-center p-3 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#2c2e42] cursor-pointer transition-colors ${!isOpen && 'justify-center'}`}
    >
      <Icon className={`w-5 h-5 flex-shrink-0 ${isOpen && 'mr-3'}`} />
      {isOpen && <span>{text}</span>}
    </div>
  );
};

export { Sidebar };