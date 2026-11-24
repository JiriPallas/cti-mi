// Service worker: aplikace se otevře i při výpadku internetu (dokumenty jsou v počítači).
const CACHE = "cti-v2";
const SOUBORY = ["./", "index.html", "manifest.webmanifest", "ikona-192.png", "ikona-512.png"];
self.addEventListener("install", e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(SOUBORY))); });
self.addEventListener("activate", e => e.waitUntil(
  self.clients.claim().then(() => caches.keys()).then(k => Promise.all(k.filter(n => n.startsWith("cti-") && n !== CACHE).map(n => caches.delete(n))))));
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;
  // nejdřív síť (aby byla vždy nejnovější verze), při výpadku uložená kopie
  // „no-cache“: vždy se zeptat serveru, jestli není novější verze (jinak až 10 minut stará kopie)
  const pozadavek = e.request.mode === "navigate"
    ? new Request(e.request.url, { cache: "no-cache", credentials: "same-origin" })
    : new Request(e.request, { cache: "no-cache" });
  e.respondWith(fetch(pozadavek).then(r => {
    if (r.ok && e.request.method === "GET") { const kopie = r.clone(); caches.open(CACHE).then(c => c.put(e.request, kopie)); }
    return r;
  }).catch(() => caches.match(e.request)));
});
