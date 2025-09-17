// Simple service worker for offline cache + outbox strategy
const CACHE_NAME = 'finance-cache-v1';
const OFFLINE_URLS = [
  '/static/index.html',
  '/static/styles.css',
  '/static/app.js',
  '/static/manifest.webmanifest',
];

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(OFFLINE_URLS);
    self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    try {
      const fresh = await fetch(request);
      cache.put(request, fresh.clone());
      return fresh;
    } catch (err) {
      return cached || new Response('Offline', { status: 503 });
    }
  })());
});
