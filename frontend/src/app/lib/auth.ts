import { cookies } from "next/headers";

export type UserRole = "admin" | "operator" | "viewer";
export type SessionUser = {
  userId: string;
  username: string;
  role: UserRole;
  exp?: number;
};

export const AUTH_COOKIE_NAME = "auth_token";

const decodeBase64 = typeof atob === "function"
  ? (value: string) => atob(value)
  : (value: string) => Buffer.from(value, "base64").toString("binary");

const encodeBase64 = typeof btoa === "function"
  ? (value: string) => btoa(value)
  : (value: string) => Buffer.from(value, "binary").toString("base64");

function getJwtSecret(): Uint8Array {
  const secret = process.env.AUTH_SECRET || process.env.NEXT_PUBLIC_AUTH_SECRET;
  if (!secret) {
    throw new Error("AUTH_SECRET must be configured for JWT verification");
  }
  return new TextEncoder().encode(secret);
}

function base64UrlDecode(segment: string): Uint8Array {
  const normalized = segment.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "=");
  const binary = decodeBase64(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

function base64UrlEncode(data: ArrayBuffer): string {
  const bytes = new Uint8Array(data);
  let binary = "";
  bytes.forEach((b) => {
    binary += String.fromCharCode(b);
  });
  return encodeBase64(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function parsePayload(payloadSegment: string): SessionUser | null {
  const decoded = new TextDecoder().decode(base64UrlDecode(payloadSegment));
  const payload = JSON.parse(decoded) as Record<string, unknown>;

  if (typeof payload.sub !== "string" || typeof payload.role !== "string") {
    return null;
  }

  return {
    userId: String(payload.user_id ?? payload.sub),
    username: payload.sub,
    role: payload.role as UserRole,
    exp: typeof payload.exp === "number" ? payload.exp : undefined,
  };
}

export async function verifyAuthToken(token: string): Promise<SessionUser | null> {
  const segments = token.split(".");
  if (segments.length !== 3) return null;

  const [headerSegment, payloadSegment, signatureSegment] = segments;
  const data = `${headerSegment}.${payloadSegment}`;

  const key = await crypto.subtle.importKey(
    "raw",
    getJwtSecret(),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const expectedSignature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(data));
  const encodedSignature = base64UrlEncode(expectedSignature);

  if (encodedSignature !== signatureSegment) {
    return null;
  }

  const user = parsePayload(payloadSegment);
  if (!user) return null;

  if (user.exp && Date.now() / 1000 > user.exp) {
    return null;
  }

  return user;
}

export async function getUserFromCookies(): Promise<SessionUser | null> {
  const token = cookies().get(AUTH_COOKIE_NAME)?.value;
  if (!token) return null;

  return verifyAuthToken(token);
}
