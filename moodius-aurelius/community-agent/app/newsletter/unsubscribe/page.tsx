

export const dynamic = "force-dynamic";

// GET shows a button (mail scanners prefetch links; a GET must not unsubscribe on its own);
// the form POSTs to the API, which does the change. One click for the human.
export default async function Unsub({ searchParams }: { searchParams: Promise<{ t?: string; done?: string }> }) {
  const { t, done } = await searchParams;
  if (done) return <main className="wrap"><h1>Unsubscribed.</h1><p>You won't receive the newsletter again. Sorry to see you go.</p></main>;
  return (
    <main className="wrap">
      <h1>Unsubscribe</h1>
      <form method="post" action="/api/newsletter/unsubscribe">
        <input type="hidden" name="t" value={t ?? ""} />
        <button className="btn" type="submit">Unsubscribe me</button>
      </form>
    </main>
  );
}
