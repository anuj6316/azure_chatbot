
export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot' | 'error';
  diagram?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  date: string;
}
