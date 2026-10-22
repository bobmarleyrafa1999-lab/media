export const dynamic = "force-dynamic";
export default async function Login({ searchParams }: { searchParams: Promise<{ msg?: string }> }) {
  const { msg } = await searchParams;
  return (
    <main className="wrap">
      <h1>Dashboard</h1>
      {msg && <p className="card">{msg}</p>}
      <form method="post" action="/api/admin/login" className="card stack">
        <label htmlFor="pw" className="small muted">Password</label>
        <input id="pw" name="password" type="password" required autoComplete="current-password" />
        <button className="btn" type="submit">Sign in</button>
      </form>
    </main>
  );
}
