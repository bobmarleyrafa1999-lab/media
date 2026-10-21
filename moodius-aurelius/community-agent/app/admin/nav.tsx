export function AdminNav({ msg }: { msg?: string }) {
  return (
    <>
      <nav className="admin">
        <strong style={{ fontFamily: "var(--serif)" }}>Moodius</strong>
        <a href="/admin">Overview</a><a href="/admin/queue">Comments</a><a href="/admin/sponsors">Sponsors</a>
        <a href="/admin/revenue">Revenue & links</a><a href="/admin/media-kit">Media kit</a><a href="/admin/settings">Settings</a>
        <form method="post" action="/api/admin/logout" style={{ marginLeft: "auto" }}><button className="btn ghost" style={{ padding: "4px 10px" }}>Log out</button></form>
      </nav>
      {msg && <div className="wide" style={{ paddingBottom: 0 }}><div className="card" role="status">{msg}</div></div>}
    </>
  );
}
export const money = (c: number | string | null | undefined, cur = "£") => `${Number(c ?? 0) < 0 ? "−" : ""}${cur}${(Math.abs(Number(c ?? 0)) / 100).toFixed(2)}`;
export const pct = (x: number | null | undefined) => (x == null ? "n/a" : `${(x * 100).toFixed(1)}%`);
