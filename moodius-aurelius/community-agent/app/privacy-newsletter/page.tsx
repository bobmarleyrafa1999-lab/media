import { CONSENT_TEXT } from "../../src/lib/newsletter";
import { config } from "../../src/lib/config";

export const metadata = { title: "Privacy" };

export default function Privacy() {
  return (
    <main className="wrap prose">
      <h1>Privacy notice</h1>
      <p className="muted small">Consent version {config().newsletter.consentVersion}</p>
      <h2>Newsletter</h2>
      <p>If you subscribe we store your email address, the exact consent wording you agreed to, its version and the time, where you signed up (for example "link in bio"), and a one-way hash of your IP address used only to stop abuse. We never store the IP itself.</p>
      <p>The consent you give: <em>"{CONSENT_TEXT}"</em></p>
      <p>Lawful basis: consent (UK GDPR art. 6(1)(a)); electronic marketing consent under PECR. You are added only after clicking the confirmation link. Once confirmed, your address is imported into Substack, which delivers the newsletter as our processor. Every email carries a one-click unsubscribe link. To have your data deleted entirely, reply to any email and ask; we'll do it within 30 days.</p>
      <h2>Instagram comments and messages</h2>
      <p>When you comment on our posts we process the comment, your public username and the post it belongs to, to reply and to understand which topics start real conversations (legitimate interests). Commenting never signs you up to email. If you comment a keyword such as JOURNAL, we send one private message with the link you asked for; that is the only message unless you reply.</p>
      <h2>Link clicks</h2>
      <p>Our links pass through our own server to count clicks per link and source. No cookies, no IP addresses, no device fingerprints.</p>
      <h2>Retention</h2>
      <p>Unconfirmed sign-ups are deleted after 30 days. Comment records are kept for 12 months, then deleted.</p>
    </main>
  );
}
