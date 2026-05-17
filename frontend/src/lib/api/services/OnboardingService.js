import { ApiClient } from '../client';

export const OnboardingService = {
  getInterviewQuestions: () => ApiClient.get('/api/onboarding/interview-questions'),
  getPersonaQuestions: () => ApiClient.get('/api/onboarding/persona-questions'),
  uploadKnowledgeFiles: (formData) => ApiClient.post('/api/onboarding/knowledge', formData),
  uploadMasterCases: (formData) => ApiClient.post('/api/onboarding/cases', formData),
  getAnalysisStatus: () => ApiClient.get('/api/onboarding/analysis-status'),
  startAnalysis: () => ApiClient.post('/api/onboarding/start-analysis'),
  submitInterviewAnswers: (answers) => ApiClient.post('/api/onboarding/interview-answers', answers),
  submitPersonaConfig: (answers) => ApiClient.post('/api/onboarding/persona-config', answers),
};
