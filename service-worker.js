/* ==============================================================
   DrumAPP · Service Worker
   Strategia: cache-first per gli asset statici,
   con caching "on-the-fly" dei font di Google quando richiesti.
   ============================================================== */

const CACHE_NAME = 'drumapp-v5';

// Asset locali della PWA
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

// ----- INSTALL: pre-carica gli asset core ----------------------
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

// ----- ACTIVATE: pulisce eventuali cache vecchie ---------------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ----- FETCH: cache-first + runtime caching per font ------------
self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  const isGoogleFont =
    url.hostname === 'fonts.googleapis.com' ||
    url.hostname === 'fonts.gstatic.com';

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;

      return fetch(req)
        .then((res) => {
          // Cachiamo al volo i font di Google e le risposte same-origin
          if (res && res.ok && (isGoogleFont || url.origin === location.origin)) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return res;
        })
        .catch(() => {
          // Fallback: se la richiesta e' un documento HTML, ritorna index.html
          if (req.destination === 'document') {
            return caches.match('./index.html');
          }
        });
    })
  );
});
