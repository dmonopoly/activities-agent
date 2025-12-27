export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function getBackendApiBaseUrl(): string {
  // Explicit override (recommended for production stability)
  if (process.env.BACKEND_API_URL) {
    return process.env.BACKEND_API_URL;
  }

  // Vercel preview: derive backend URL from this frontend's branch URL
  // Frontend: activities-agent-frontend-*.vercel.app
  // Backend:  activities-agent-api-*.vercel.app
  if (process.env.VERCEL_ENV === "preview" && process.env.VERCEL_BRANCH_URL) {
    const backendHost = process.env.VERCEL_BRANCH_URL.replace(
      "activities-agent-frontend",
      "activities-agent-api"
    );
    return `https://${backendHost}/api`;
  }

  // Vercel production: default to known production backend
  if (process.env.VERCEL_ENV === "production") {
    return "https://activities-agent-api.vercel.app/api";
  }

  // Local development fallback
  return "http://localhost:8000/api";
}

async function proxy(request: Request, pathParts: string[]): Promise<Response> {
  const backendBase = getBackendApiBaseUrl().replace(/\/+$/, "");
  const path = pathParts.join("/");

  const incomingUrl = new URL(request.url);
  const targetUrl = `${backendBase}/${path}${incomingUrl.search}`;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");

  // Preview-only shared secret: injected server-side so it never reaches the browser.
  if (process.env.VERCEL_ENV === "preview") {
    const token = process.env.PREVIEW_API_TOKEN;
    if (!token) {
      return Response.json(
        { error: "Missing PREVIEW_API_TOKEN in frontend environment." },
        { status: 500 }
      );
    }
    headers.set("X-Preview-Token", token);
  }

  const method = request.method.toUpperCase();
  const body =
    method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();

  const upstream = await fetch(targetUrl, {
    method,
    headers,
    body,
    redirect: "manual",
  });

  // Pass through response (including status + body). Avoid passing hop-by-hop headers.
  const respHeaders = new Headers(upstream.headers);
  respHeaders.delete("connection");
  respHeaders.delete("keep-alive");
  respHeaders.delete("proxy-authenticate");
  respHeaders.delete("proxy-authorization");
  respHeaders.delete("te");
  respHeaders.delete("trailer");
  respHeaders.delete("transfer-encoding");
  respHeaders.delete("upgrade");

  return new Response(upstream.body, {
    status: upstream.status,
    headers: respHeaders,
  });
}

export async function GET(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  return proxy(request, params.path);
}
export async function POST(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  return proxy(request, params.path);
}
export async function PUT(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  return proxy(request, params.path);
}
export async function PATCH(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  return proxy(request, params.path);
}
export async function DELETE(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  return proxy(request, params.path);
}
export async function OPTIONS(
  request: Request,
  { params }: { params: { path: string[] } }
) {
  return proxy(request, params.path);
}


