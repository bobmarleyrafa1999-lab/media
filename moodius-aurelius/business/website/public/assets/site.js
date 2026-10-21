// Moodius Aurelius — progressive enhancement only; every form works without JavaScript.
// Attribution without cookies or storage: the campaign source rides along in the URL
// (?src=...) and is copied into internal links and forms on the page.
(function () {
  var params = new URLSearchParams(location.search);
  var src = (params.get("src") || params.get("utm_source") || "").toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 40);
  var page = document.body.getAttribute("data-page");

  if (src) {
    document.querySelectorAll('a[href^="/"]').forEach(function (a) {
      if (a.hasAttribute("data-no-src")) return;
      var u = new URL(a.getAttribute("href"), location.origin);
      if (!u.searchParams.has("src")) u.searchParams.set("src", src);
      a.setAttribute("href", u.pathname + u.search + u.hash);
    });
  }
  document.querySelectorAll('input[name="src"], input[name="source"][data-from-src]').forEach(function (i) {
    if (src) i.value = i.name === "source" ? (i.value ? i.value + "_" : "") + src : src;
  });

  // Cookieless page counter: page name + source, nothing about the visitor.
  if (page && navigator.sendBeacon) {
    try { navigator.sendBeacon("/api/shop/event", new Blob([JSON.stringify({ kind: "page_view", slug: page, src: src || null })], { type: "application/json" })); } catch (e) {}
  }

  // Messages passed back by form redirects.
  var box = document.querySelector("[data-notice]");
  if (box) {
    var msg = params.get("error");
    if (msg) { box.textContent = msg; box.className = "notice error"; box.hidden = false; }
    else if (params.get("cancelled")) { box.textContent = "Checkout cancelled. Nothing was charged."; box.className = "notice"; box.hidden = false; }
    else if (params.get("sent")) { box.textContent = box.getAttribute("data-sent") || "Done. Check your inbox."; box.className = "notice"; box.hidden = false; }
  }

  // Buy button stays disabled until the digital-content consent box is ticked.
  document.querySelectorAll("form[data-buy]").forEach(function (f) {
    var box = f.querySelector('input[name="consent"]');
    var btn = f.querySelector('button[type="submit"]');
    var sync = function () { btn.disabled = !box.checked; };
    box.addEventListener("change", sync); sync();
    f.addEventListener("submit", function () { btn.disabled = true; btn.textContent = "Opening secure checkout…"; });
  });

  // Thank-you page: wait for the payment confirmation, then show the download button.
  var ty = document.querySelector("[data-thankyou]");
  if (ty) {
    var ref = params.get("ref");
    var tries = 0;
    var show = function (id) { ty.querySelectorAll("[data-state]").forEach(function (el) { el.hidden = el.getAttribute("data-state") !== id; }); };
    var poll = function () {
      if (!ref) return show("unknown");
      fetch("/api/shop/order-status?ref=" + encodeURIComponent(ref), { cache: "no-store" })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.status === "paid") {
            ty.querySelector("[data-email]").textContent = d.email || "your email";
            ty.querySelector("[data-order]").textContent = d.orderId + (d.testMode ? " · test order, no money taken" : "");
            var a = ty.querySelector("[data-download]");
            if (d.downloadUrl) { a.href = d.downloadUrl; a.hidden = false; } else { a.hidden = true; }
            show("paid");
          } else if (d.status === "pending" && tries++ < 30) { setTimeout(poll, 2000); }
          else if (d.status === "pending") { show("slow"); }
          else if (d.status === "refunded") { show("refunded"); }
          else { show("unknown"); }
        })
        .catch(function () { if (tries++ < 30) setTimeout(poll, 3000); else show("slow"); });
    };
    poll();
  }
})();
