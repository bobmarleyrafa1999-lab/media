// Back office: reads /api/shop/admin/* with the admin token held in sessionStorage for this tab only.
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var token = "";
  try { token = sessionStorage.getItem("mo_admin") || ""; } catch (e) {}
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var money = function (c, cur) { return new Intl.NumberFormat("en-GB", { style: "currency", currency: cur || "GBP" }).format((c || 0) / 100); };
  var api = function (path, opts) {
    opts = opts || {};
    opts.headers = { authorization: "Bearer " + token };
    return fetch("/api/shop/admin/" + path, opts).then(function (r) { if (r.status === 401) throw new Error("Wrong token"); return r.json(); });
  };
  var table = function (el, cols, rows) {
    el.innerHTML = "<tr>" + cols.map(function (c) { return "<th>" + esc(c[0]) + "</th>"; }).join("") + "</tr>" +
      rows.map(function (r) { return "<tr>" + cols.map(function (c) { return "<td>" + esc(c[1](r)) + "</td>"; }).join("") + "</tr>"; }).join("");
  };
  var load = function () {
    var days = $("bo-days").value;
    api("summary?days=" + days).then(function (s) {
      var t = s.totals || {};
      $("bo-stats").innerHTML = [["Link clicks", t.link_click], ["Product views", t.page_view], ["Checkouts", t.checkout_started], ["Purchases", t.purchase], ["Subscribes", t.subscribe]]
        .map(function (x) { return "<div><b>" + (x[1] || 0) + "</b>" + x[0] + "</div>"; }).join("");
      table($("bo-src"), [["Source", function (r) { return r.src; }], ["Clicks", function (r) { return r.clicks; }], ["Product views", function (r) { return r.product_views; }], ["Checkouts", function (r) { return r.checkouts; }], ["Purchases", function (r) { return r.purchases; }], ["Subscribes", function (r) { return r.subscribes; }]], s.by_source || []);
      table($("bo-rev"), [["Mode", function (r) { return r.test_mode ? "test" : "live"; }], ["Orders", function (r) { return r.orders; }], ["Refunds", function (r) { return r.refunds; }], ["Net", function (r) { return money(r.net_cents, r.currency); }]], s.revenue || []);
    });
    api("orders").then(function (d) {
      table($("bo-orders"), [["When", function (r) { return r.created_at.slice(0, 16).replace("T", " "); }], ["Order", function (r) { return r.id; }], ["Email", function (r) { return r.email; }], ["Product", function (r) { return r.product_slug; }], ["Paid", function (r) { return money(r.amount_cents, r.currency); }], ["Status", function (r) { return r.status + (r.test_mode ? " (test)" : ""); }], ["Source", function (r) { return r.src || ""; }], ["Synced", function (r) { return r.revenue_sent_at ? "yes" : "no"; }]], d.orders || []);
    });
    api("outbox").then(function (d) {
      table($("bo-outbox"), [["When", function (r) { return r.created_at.slice(0, 16).replace("T", " "); }], ["To", function (r) { return r.to_addr; }], ["Subject", function (r) { return r.subject; }], ["Kind", function (r) { return r.kind; }], ["Status", function (r) { return r.error || r.provider; }]], d.outbox || []);
    });
  };
  var open = function () { $("bo-login").hidden = true; $("bo").hidden = false; load(); };
  $("bo-login").addEventListener("submit", function (e) {
    e.preventDefault(); token = $("bo-token").value.trim();
    api("summary?days=1").then(function () { try { sessionStorage.setItem("mo_admin", token); } catch (e) {} open(); }).catch(function (err) { alert(err.message); });
  });
  $("bo-days").addEventListener("change", load);
  $("bo-export").addEventListener("click", function () {
    api("export").then(function (d) {
      var a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(d, null, 2)], { type: "application/json" }));
      a.download = "moodius-export-" + new Date().toISOString().slice(0, 10) + ".json"; a.click();
    });
  });
  $("bo-forward").addEventListener("click", function () { api("forward-pending", { method: "POST" }).then(function (d) { alert(JSON.stringify(d.results)); load(); }); });
  if (token) open();
})();
