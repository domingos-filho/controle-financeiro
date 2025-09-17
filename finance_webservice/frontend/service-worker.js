const CACHE = 'finance-cache-v1';
const ASSETS = ['/', '/index.html', '/app.js', '/manifest.json'];
self.addEventListener('install', e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));
});
self.addEventListener('fetch', e=>{
  const url = new URL(e.request.url);
  if(url.pathname.startsWith('/api/')){
    return; // let network, app handles offline queue
  }
  e.respondWith(
    caches.match(e.request).then(resp=> resp || fetch(e.request).then(f=>{
      const copy = f.clone();
      caches.open(CACHE).then(c=>c.put(e.request, copy));
      return f;
    }).catch(()=>caches.match('/index.html')))
  );
});
