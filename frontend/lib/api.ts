const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ChatResponse {
  session_id: string;
  question: string;
  intent?: string;
  answer: string;
  data: Record<string, unknown>[];
  graph_data: Record<string, unknown>[];
  chart?: ChartSpec | null;
  cube_query?: Record<string, unknown>;
  sources: string[];
  validation?: string;
  error?: string;
}

export interface ChartSpec {
  type: "bar" | "line" | "pie" | "scatter";
  data: Record<string, unknown>[];
  xKey: string;
  yKeys: string[];
  title: string;
}

export async function sendChat(question: string, sessionId?: string, userRole?: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, session_id: sessionId, user_role: userRole || "analyst" }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json();
}

export async function executeQuery(query: Record<string, unknown>) {
  const res = await fetch(`${API_BASE}/api/v1/analytics/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      measures: query.measures,
      dimensions: query.dimensions || [],
      filters: query.filters || [],
      timeDimensions: query.timeDimensions || [],
      limit: query.limit || 10,
    }),
  });
  if (!res.ok) return null;
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/api/v1/health`);
  return res.json();
}

export async function getMeasures() {
  const res = await fetch(`${API_BASE}/api/v1/analytics/measures`);
  return res.json();
}
