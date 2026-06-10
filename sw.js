const CACHE_NAME = 'xiaochao-v1';
const ASSETS = ['/', '/manifest.json'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  if (e.request.url.includes('/api/')) return; // API 不缓存
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
