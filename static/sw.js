// Service worker do Placar do Dominó — app shell offline-first.
// Bump CACHE a cada mudança de assets pra invalidar a versão antiga.
const CACHE = 'domino-v3';
const ASSETS = [
  './',
  'index.html',
  'manifest.webmanifest',
  'fonts/anton-latin.woff2',
  'fonts/archivo-latin.woff2',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/icon-180.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  // cross-origin (ex.: beacon de analytics do CF) fica com o browser
  if (new URL(req.url).origin !== location.origin) return;

  // navegação: rede primeiro (pega updates), cache como fallback offline
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then(resp => {
          const copy = resp.clone();
          caches.open(CACHE).then(c => c.put('index.html', copy));
          return resp;
        })
        .catch(() => caches.match('index.html'))
    );
    return;
  }

  // demais assets: cache primeiro
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(resp => {
      if (resp.ok && new URL(req.url).origin === location.origin) {
        const copy = resp.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
      }
      return resp;
    }))
  );
});
