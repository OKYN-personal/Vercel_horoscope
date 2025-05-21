// PWA対応のための Service Worker 登録
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(function(registration) {
        console.log('Service Worker登録成功:', registration.scope);
      })
      .catch(function(error) {
        console.log('Service Worker登録失敗:', error);
      });
  });
} 