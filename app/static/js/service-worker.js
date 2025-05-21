// キャッシュ名（バージョン管理用）
const CACHE_NAME = 'horoscope-app-v1';

// キャッシュするリソースの一覧
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png'
];

// Service Workerのインストール時
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('キャッシュを開きました');
        return cache.addAll(urlsToCache);
      })
  );
});

// Service Workerのアクティベート時
self.addEventListener('activate', function(event) {
  const cacheWhitelist = [CACHE_NAME];
  
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// ネットワークリクエスト時
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // キャッシュ内に該当レスポンスがあれば、それを返す
        if (response) {
          return response;
        }
        return fetch(event.request)
          .then(function(response) {
            // レスポンスが正しくない場合は何もしない
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // レスポンスをキャッシュに入れるためにコピーする
            var responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(function(cache) {
                cache.put(event.request, responseToCache);
              });

            return response;
          });
      })
  );
});

// プッシュ通知を受信した時
self.addEventListener('push', function(event) {
  console.log('プッシュイベントを受信しました。', event);
  
  let notificationData = {};
  
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData = {
        title: 'ホロスコープ通知',
        body: event.data.text()
      };
    }
  } else {
    notificationData = {
      title: 'ホロスコープ通知',
      body: '新しい天文イベントがあります。'
    };
  }
  
  const options = {
    body: notificationData.body || '詳細はアプリをご確認ください。',
    icon: notificationData.icon || '/static/icons/icon-192x192.png',
    badge: '/static/icons/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: notificationData.url || '/',
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: '詳細を見る',
        icon: '/static/icons/check.png'
      },
      {
        action: 'close',
        title: '閉じる',
        icon: '/static/icons/close.png'
      },
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// 通知クリック時
self.addEventListener('notificationclick', function(event) {
  console.log('通知がクリックされました。', event);
  
  // 通知を閉じる
  event.notification.close();
  
  // アクション（ボタン）のチェック
  if (event.action === 'explore') {
    console.log('「詳細を見る」ボタンがクリックされました。');
  } else if (event.action === 'close') {
    console.log('「閉じる」ボタンがクリックされました。');
    return;
  }
  
  // 通知データからURLを取得
  const urlToOpen = event.notification.data?.url || '/';
  
  // クリック時の振る舞い: URLを開く
  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(function(clientList) {
      // すでに開いているウィンドウがあればそれをフォーカス
      for (let i = 0; i < clientList.length; i++) {
        const client = clientList[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // なければ新しいウィンドウを開く
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});

// Background Sync
self.addEventListener('sync', function(event) {
  console.log('バックグラウンド同期イベント受信:', event);
  
  if (event.tag === 'sync-horoscope-data') {
    event.waitUntil(syncHoroscopeData());
  } else if (event.tag === 'sync-user-settings') {
    event.waitUntil(syncUserSettings());
  }
});

// オフラインデータの同期処理
async function syncHoroscopeData() {
  try {
    const offlineData = await getOfflineData();
    
    if (offlineData && offlineData.length > 0) {
      console.log('オフラインデータを同期します:', offlineData.length + '件');
      
      // サーバーにデータを送信
      const syncResults = await Promise.all(
        offlineData.map(data => 
          fetch('/api/sync_horoscope_data', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
          })
          .then(response => {
            if (response.ok) {
              return { id: data.id, success: true };
            }
            return { id: data.id, success: false };
          })
          .catch(err => {
            console.error('同期エラー:', err);
            return { id: data.id, success: false };
          })
        )
      );
      
      // 成功したデータをオフラインストアから削除
      const successIds = syncResults
        .filter(result => result.success)
        .map(result => result.id);
      
      if (successIds.length > 0) {
        await removeOfflineData(successIds);
        console.log('同期完了:', successIds.length + '件');
      }
    }
  } catch (error) {
    console.error('同期中にエラーが発生しました:', error);
    throw error; // 同期を失敗させて再試行させる
  }
}

// ユーザー設定の同期処理
async function syncUserSettings() {
  try {
    const offlineSettings = await getOfflineSettings();
    
    if (offlineSettings) {
      console.log('オフライン設定を同期します');
      
      // サーバーに設定を送信
      const response = await fetch('/api/sync_user_settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(offlineSettings)
      });
      
      if (response.ok) {
        await clearOfflineSettings();
        console.log('設定の同期完了');
      }
    }
  } catch (error) {
    console.error('設定の同期中にエラーが発生しました:', error);
    throw error; // 同期を失敗させて再試行させる
  }
}

// オフラインデータの取得
async function getOfflineData() {
  // IndexedDBやLocalStorageからオフラインデータを取得する実装
  // 仮実装
  const offlineDataStr = localStorage.getItem('offlineHoroscopeData');
  return offlineDataStr ? JSON.parse(offlineDataStr) : [];
}

// オフラインデータの削除
async function removeOfflineData(ids) {
  // 成功したIDのデータを削除する実装
  // 仮実装
  const offlineDataStr = localStorage.getItem('offlineHoroscopeData');
  if (offlineDataStr) {
    const offlineData = JSON.parse(offlineDataStr);
    const newData = offlineData.filter(item => !ids.includes(item.id));
    localStorage.setItem('offlineHoroscopeData', JSON.stringify(newData));
  }
}

// オフライン設定の取得
async function getOfflineSettings() {
  // 仮実装
  const settingsStr = localStorage.getItem('offlineUserSettings');
  return settingsStr ? JSON.parse(settingsStr) : null;
}

// オフライン設定のクリア
async function clearOfflineSettings() {
  // 仮実装
  localStorage.removeItem('offlineUserSettings');
} 