import { ApiClient } from '../client';

export const ChatService = {
  sendMessage: (payload) => ApiClient.post('/api/chat/message', payload),
  setOverride: (payload) => ApiClient.post('/api/chat/override', payload),
  sendExpertMessage: (payload) => ApiClient.post('/api/chat/expert-message', payload),
  getHistory: (sessionId) => ApiClient.get(`/api/chat/history?session_id=${sessionId}`)
};
