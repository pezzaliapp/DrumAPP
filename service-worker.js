/* ==============================================================
   DrumAPP · Service Worker v9
   Strategia:
     - network-first per HTML/JS/CSS/JSON (gli aggiornamenti arrivano subito)
     - cache-first per icone e font (stabili, risparmia banda)
     - fallback su cache se offline
     - skipWaiting + clients.claim -> aggiornamento immediato al deploy
   ============================================================== */

const CACHE_NAME = 'drumapp-v9';

// Asset locali precaricati all'install
const CORE_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-192-maskable.png',
  './icons/icon-512-maskable.png'
];

// ----- INSTALL: pre-carica gli asset core -----------------------
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  // Attiva subito la nuova versione senza aspettare la chiusura tab
  self.skipWaiting();
});

// ----- ACTIVATE: pulisce cache vecchie e prende controllo -------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ----- MESSAGE: permette alla pagina di forzare skipWaiting ------
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

// ----- FETCH: strategie differenziate ---------------------------
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  const isGoogleFont =
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com';

  const isSameOrigin = url.origin === location.origin;

  // Asset che cambiano spesso: HTML, JS, CSS, JSON (demo library)
  // -> NETWORK FIRST: prova la rete, cache come fallback
  const isVolatile =
    isSameOrigin && (
      req.destination === 'document' ||
      req.destination === 'script'   ||
      req.destination === 'style'    ||
      url.pathname.endsWith('.json') ||
      url.pathname.endsWith('.html') ||
      url.pathname.endsWith('.js')   ||
      url.pathname.endsWith('.css')
    );

  if (isVolatile) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          // Salva in cache la risposta fresca
          if (res && res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return res;
        })
        .catch(() => {
          // Offline -> cache fallback
          return caches.match(req).then((cached) => {
            if (cached) return cached;
            if (req.destination === 'document') {
              return caches.match('./index.html');
            }
          });
        })
    );
    return;
  }

  // Asset stabili: icone, immagini, font -> CACHE FIRST
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;

      return fetch(req)
        .then((res) => {
          if (res && res.ok && (isGoogleFont || isSameOrigin)) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return res;
        })
        .catch(() => {
          if (req.destination === 'document') {
            return caches.match('./index.html');
          }
        });
    })
  );
});
