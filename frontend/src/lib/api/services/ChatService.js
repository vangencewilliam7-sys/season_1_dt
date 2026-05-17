import { ApiClient } from '../client';

export const ChatService = {
  sendMessage: (payload) => ApiClient.post('/api/chat/message', payload)
};
