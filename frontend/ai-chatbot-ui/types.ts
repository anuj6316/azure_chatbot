
export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot' | 'error';
}

export interface ChatSession {
  id: string;
  title: string;
  date: string;
}
