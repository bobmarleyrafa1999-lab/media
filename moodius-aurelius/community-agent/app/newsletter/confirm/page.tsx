import { confirm } from "../../../src/lib/newsletter";

export const dynamic = "force-dynamic";

export default async function Confirm({ searchParams }: { searchParams: Promise<{ t?: string }> }) {
  const { t } = await searchParams;
  const r = t ? await confirm(t) : { ok: false, leadMagnet: null };
  return (
    <main className="wrap">
      <h1>{r.ok ? "You're in." : "That link didn't work."}</h1>
      {r.ok ? (
        <>
          <p>Thank you for confirming. The next essay will reach you on publication day.</p>
          {r.leadMagnet && <p><a className="btn ember" href={r.leadMagnet.url}>Download {r.leadMagnet.title.replace(/^The /, "the ")}</a></p>}
          <p className="muted small">Every email has a one-click unsubscribe link.</p>
        </>
      ) : (
        <p>It may have been used already or have expired. <a href="/newsletter">Subscribe again</a>; nothing is sent until you confirm.</p>
      )}
    </main>
  );
}
