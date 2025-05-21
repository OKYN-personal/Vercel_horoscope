// インストールプロンプトを保存する変数
let deferredPrompt;
const installBanner = document.createElement('div');
installBanner.className = 'app-install-banner';
installBanner.innerHTML = `
    <p>ホロスコープアプリをインストールしますか？オフラインでも使えるようになります。</p>
    <button id="install-btn" class="btn btn-primary">インストール</button>
    <button id="dismiss-btn" class="btn btn-secondary">あとで</button>
`;

// beforeinstallpromptイベントをリッスン
window.addEventListener('beforeinstallprompt', (e) => {
  // Chromeのデフォルト表示をキャンセル
  e.preventDefault();
  // 後で使うためにイベントを保存
  deferredPrompt = e;
  // インストールバナーをDOMに追加
  document.body.appendChild(installBanner);
  installBanner.classList.add('show');
  
  // インストールボタンのクリックイベント
  document.getElementById('install-btn').addEventListener('click', (e) => {
    // バナーを非表示
    installBanner.classList.remove('show');
    // インストールプロンプトを表示
    deferredPrompt.prompt();
    // ユーザーの選択を待つ
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('ユーザーがアプリをインストールしました');
      } else {
        console.log('ユーザーがインストールをキャンセルしました');
      }
      // イベントを破棄
      deferredPrompt = null;
    });
  });
  
  // あとでボタンのクリックイベント
  document.getElementById('dismiss-btn').addEventListener('click', (e) => {
    // バナーを非表示
    installBanner.classList.remove('show');
  });
});

// アプリがインストール済みの場合
window.addEventListener('appinstalled', (evt) => {
  console.log('アプリがインストールされました！');
});

// オフライン状態の検知
window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

function updateOnlineStatus(event) {
  const offlineNotice = document.querySelector('.offline-mode') || createOfflineNotice();
  
  if (navigator.onLine) {
    offlineNotice.classList.remove('show');
  } else {
    offlineNotice.classList.add('show');
  }
}

function createOfflineNotice() {
  const notice = document.createElement('div');
  notice.className = 'offline-mode';
  notice.textContent = 'オフラインモードです。一部の機能が制限されています。';
  document.body.insertBefore(notice, document.body.firstChild);
  return notice;
}

// 初期状態のチェック
document.addEventListener('DOMContentLoaded', function() {
  if (!navigator.onLine) {
    updateOnlineStatus();
  }
}); 