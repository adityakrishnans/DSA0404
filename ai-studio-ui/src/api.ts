const API_BASE = 'http://127.0.0.1:8050/api';

export async function fetchApi<T>(endpoint: string): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) {
      const relRes = await fetch(`/api${endpoint}`);
      if (!relRes.ok) {
        throw new Error(`API error: ${res.statusText}`);
      }
      return await relRes.json();
    }
    return await res.json();
  } catch (err) {
    const relRes = await fetch(`/api${endpoint}`);
    if (!relRes.ok) {
      throw err;
    }
    return await relRes.json();
  }
}
