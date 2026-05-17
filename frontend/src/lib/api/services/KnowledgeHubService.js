import { ApiClient } from '../client';

export const KnowledgeHubService = {
  ingestDocument: (formData) => ApiClient.post('/api/ingest', formData),
  getDocumentState: (documentId) => ApiClient.get(`/api/state/${documentId}`),
  getDocumentInfo: (documentId) => ApiClient.get(`/api/file-info/${documentId}`),
  commitResolution: (scenarioId, decision, archetype = 'Safety') => 
    ApiClient.post(`/api/commit?scenario_id=${scenarioId}&expert_decision=${encodeURIComponent(decision)}&archetype=${archetype}`)
};
