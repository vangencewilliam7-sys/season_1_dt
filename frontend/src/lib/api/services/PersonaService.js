export const PersonaService = {
  getProfile: async () => {
    const res = await fetch('/api/persona');
    if (!res.ok) throw new Error('Failed to fetch persona data');
    return res.json();
  }
};
