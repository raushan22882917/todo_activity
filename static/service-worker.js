self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open('static-cache-v1').then((cache) => {
            return cache.addAll([
                '/',
                '/static/style.css',
                '/static/icons/icon-192x192.png',
                '/static/icons/icon-512x512.png',
                '/manifest.json'
            ]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
