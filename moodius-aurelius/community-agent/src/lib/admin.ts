import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SESSION_COOKIE, sessionValid } from "./auth";

export async function isAdmin(): Promise<boolean> {
  const c = await cookies();
  return sessionValid(c.get(SESSION_COOKIE)?.value);
}

export async function requireAdmin() {
  if (!(await isAdmin())) redirect("/admin/login");
}

export function formNumber(v: FormDataEntryValue | null): number {
  const n = Number(String(v ?? "").replace(/[£€,\s]/g, ""));
  return Number.isFinite(n) ? n : NaN;
}
