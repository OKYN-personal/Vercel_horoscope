const CACHE_NAME = 'horoscope-cache-v1';
const URLS_TO_CACHE = [
  '/',
  '/static/index.html',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// インストール時にリソースをキャッシュ
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('キャッシュを開きました');
        return cache.addAll(URLS_TO_CACHE);
      })
  );
});

// フェッチイベントの処理
self.addEventListener('fetch', event => {
  // APIリクエストの場合はネットワークファーストで対応
  if (event.request.url.includes('/calculate') || 
      event.request.url.includes('/warmup') || 
      event.request.url.includes('/health')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return new Response(
            JSON.stringify({ error: 'オフラインです。インターネット接続を確認してください。' }),
            { headers: { 'Content-Type': 'application/json' } }
          );
        })
    );
    return;
  }

  // 静的アセットはキャッシュファーストで対応
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request)
          .then(response => {
            // 無効なレスポンスは処理しない
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // レスポンスを複製してキャッシュとブラウザに返す
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
            return response;
          })
          .catch(() => {
            // オフラインフォールバック
            return new Response(
              '<html><body><h1>オフラインです</h1><p>インターネット接続がありません。</p></body></html>',
              { headers: { 'Content-Type': 'text/html' } }
            );
          });
      })
  );
});

// 古いキャッシュの削除
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
}); 