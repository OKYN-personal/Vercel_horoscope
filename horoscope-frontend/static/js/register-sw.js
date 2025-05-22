// サービスワーカーがサポートされているか確認
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/js/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker登録成功:', registration.scope);
      })
      .catch(error => {
        console.log('ServiceWorker登録失敗:', error);
      });
  });

  // インストールプロンプト表示の処理
  let deferredPrompt;
  const installButton = document.getElementById('installApp');

  // インストールボタンを初期状態では非表示に
  if (installButton) {
    installButton.style.display = 'none';
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    // プロンプト表示をいったん防止
    e.preventDefault();
    // イベントを保存
    deferredPrompt = e;
    // インストールボタンがあれば表示
    if (installButton) {
      installButton.style.display = 'block';
      
      installButton.addEventListener('click', () => {
        // インストールボタンを隠す
        installButton.style.display = 'none';
        // インストールプロンプトを表示
        deferredPrompt.prompt();
        // ユーザーの選択を待つ
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            console.log('アプリがインストールされました');
          } else {
            console.log('アプリのインストールが拒否されました');
          }
          deferredPrompt = null;
        });
      });
    }
  });
} 