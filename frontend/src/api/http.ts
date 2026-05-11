const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string | null;

  constructor(status: number, message: string, detail: string | null = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function apiUrl(path: string): string {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${normalized}`;
}

async function readErrorDetail(res: Response): Promise<string | null> {
  const text = await res.text();
  if (!text) return null;
  try {
    const body = JSON.parse(text) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    return text;
  } catch {
    return text;
  }
}

export async function apiGetJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path));
  if (!res.ok) {
    const detail = await readErrorDetail(res);
    throw new ApiError(res.status, res.statusText, detail);
  }
  return (await res.json()) as T;
}

export async function apiPostJson<T, B>(path: string, body: B): Promise<T> {
  const res = await fetch(apiUrl(path), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await readErrorDetail(res);
    throw new ApiError(res.status, res.statusText, detail);
  }
  return (await res.json()) as T;
}

export async function apiDelete(path: string): Promise<void> {
  const res = await fetch(apiUrl(path), { method: "DELETE" });
  if (!res.ok) {
    const detail = await readErrorDetail(res);
    throw new ApiError(res.status, res.statusText, detail);
  }
}

export async function apiPostJsonRaw(path: string): Promise<unknown> {
  const res = await fetch(apiUrl(path), { method: "POST" });
  if (!res.ok) {
    const detail = await readErrorDetail(res);
    throw new ApiError(res.status, res.statusText, detail);
  }
  return await res.json();
}
