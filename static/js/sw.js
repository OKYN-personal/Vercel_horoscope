// サービスワーカーバージョン
const CACHE_VERSION = 'v1.0.0';

// キャッシュするファイル
const CACHE_FILES = [
    '/',
    '/static/index.html',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/help.js',
    '/static/offline.html',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/manifest.json'
];

// インストール時のキャッシュ作成
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_VERSION)
            .then((cache) => {
                console.log('キャッシュを開いています');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => {
                console.log('キャッシュの初期化が完了しました');
                return self.skipWaiting();
            })
    );
});

// 古いキャッシュの削除
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_VERSION) {
                    console.log('古いキャッシュを削除します:', key);
                    return caches.delete(key);
                }
            }));
        })
        .then(() => {
            console.log('新しいサービスワーカーがアクティブになりました');
            return self.clients.claim();
        })
    );
});

// フェッチイベントの処理
self.addEventListener('fetch', (event) => {
    // APIリクエストはネットワークファーストで処理
    if (event.request.url.includes('/api/')) {
        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return caches.match('/static/offline.html');
                })
        );
        return;
    }

    // 通常のリクエストはキャッシュファーストで処理
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // キャッシュにあればそれを返す
                if (response) {
                    return response;
                }
                
                // キャッシュになければネットワークから取得
                return fetch(event.request)
                    .then((response) => {
                        // 有効なレスポンスでなければそのまま返す
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // レスポンスをクローンしてキャッシュに保存
                        const responseToCache = response.clone();
                        caches.open(CACHE_VERSION)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });
                            
                        return response;
                    })
                    .catch(() => {
                        // オフラインの場合はオフラインページを表示
                        if (event.request.headers.get('accept').includes('text/html')) {
                            return caches.match('/static/offline.html');
                        }
                    });
            })
    );
}); 