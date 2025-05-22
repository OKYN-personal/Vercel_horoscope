// ホロスコープ計算アプリのメインスクリプト
document.addEventListener('DOMContentLoaded', () => {
    // 要素の取得
    const form = document.getElementById('horoscopeForm');
    const geolocateBtn = document.getElementById('geolocateBtn');
    const resultContainer = document.getElementById('resultContainer');
    const resultDiv = document.getElementById('result');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const offlineMessage = document.getElementById('offlineMessage');
    const installPrompt = document.getElementById('installPrompt');
    const installBtn = document.getElementById('installBtn');
    const connectionStatus = document.getElementById('connection-status');

    // 位置情報取得ボタンのイベントリスナー
    geolocateBtn.addEventListener('click', () => {
        if (navigator.geolocation) {
            loadingIndicator.classList.remove('hidden');
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    document.getElementById('latitude').value = position.coords.latitude.toFixed(6);
                    document.getElementById('longitude').value = position.coords.longitude.toFixed(6);
                    loadingIndicator.classList.add('hidden');
                },
                (error) => {
                    alert('位置情報の取得に失敗しました: ' + error.message);
                    loadingIndicator.classList.add('hidden');
                }
            );
        } else {
            alert('お使いのブラウザは位置情報をサポートしていません');
        }
    });

    // フォーム送信イベントリスナー
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // オフラインチェック
        if (!navigator.onLine) {
            offlineMessage.classList.remove('hidden');
            return;
        }
        
        // 入力データの取得
        const birthDate = document.getElementById('birthDate').value;
        const birthTime = document.getElementById('birthTime').value;
        const latitude = document.getElementById('latitude').value;
        const longitude = document.getElementById('longitude').value;
        
        // バリデーション
        if (!birthDate || !birthTime || !latitude || !longitude) {
            alert('すべてのフィールドを入力してください');
            return;
        }
        
        // ローディング表示
        loadingIndicator.classList.remove('hidden');
        resultContainer.classList.add('hidden');
        
        try {
            // APIリクエスト
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    birthDate,
                    birthTime,
                    latitude,
                    longitude
                })
            });
            
            // レスポンス処理
            if (response.ok) {
                const data = await response.json();
                displayResult(data.result);
                
                // 結果をローカルストレージに保存（オフライン対応）
                saveResultToLocalStorage(data);
            } else {
                const errorData = await response.json();
                alert('エラーが発生しました: ' + (errorData.error || '不明なエラー'));
            }
        } catch (error) {
            alert('通信エラーが発生しました: ' + error.message);
        } finally {
            loadingIndicator.classList.add('hidden');
        }
    });

    // 結果表示関数
    function displayResult(result) {
        // 結果をHTML形式で表示
        let htmlContent = `
            <div class="result-summary">
                <p><strong>太陽サイン:</strong> ${result.sun_sign}</p>
                <p><strong>月サイン:</strong> ${result.moon_sign}</p>
                <p><strong>上昇宮（アセンダント）:</strong> ${result.ascendant}</p>
            </div>
            
            <h3>惑星の位置</h3>
            <table class="result-table">
                <thead>
                    <tr>
                        <th>惑星</th>
                        <th>星座</th>
                        <th>度数</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        // 惑星データの追加
        result.planets.forEach(planet => {
            htmlContent += `
                <tr>
                    <td>${planet.name}</td>
                    <td>${planet.sign}</td>
                    <td>${planet.degree}</td>
                </tr>
            `;
        });
        
        htmlContent += `
                </tbody>
            </table>
            
            <h3>アスペクト</h3>
            <ul class="aspect-list">
        `;
        
        // アスペクトデータの追加
        result.aspects.forEach(aspect => {
            htmlContent += `
                <li>${aspect.point1} ${aspect.type} ${aspect.point2} (オーブ: ${aspect.orb})</li>
            `;
        });
        
        htmlContent += `
            </ul>
        `;
        
        // 結果の表示
        resultDiv.innerHTML = htmlContent;
        resultContainer.classList.remove('hidden');
    }

    // ローカルストレージに結果を保存
    function saveResultToLocalStorage(data) {
        try {
            const savedResults = JSON.parse(localStorage.getItem('horoscopeResults') || '[]');
            savedResults.push({
                id: Date.now(),
                timestamp: data.timestamp,
                input: {
                    birthDate: document.getElementById('birthDate').value,
                    birthTime: document.getElementById('birthTime').value,
                    latitude: document.getElementById('latitude').value,
                    longitude: document.getElementById('longitude').value
                },
                result: data.result
            });
            
            // 最大10件まで保存
            if (savedResults.length > 10) {
                savedResults.shift();
            }
            
            localStorage.setItem('horoscopeResults', JSON.stringify(savedResults));
        } catch (error) {
            console.error('結果の保存に失敗しました:', error);
        }
    }

    // オンライン/オフライン状態の監視
    function updateOnlineStatus() {
        if (navigator.onLine) {
            connectionStatus.textContent = 'オンライン';
            connectionStatus.className = 'online';
            offlineMessage.classList.add('hidden');
        } else {
            connectionStatus.textContent = 'オフライン';
            connectionStatus.className = 'offline';
            offlineMessage.classList.remove('hidden');
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();

    // PWAインストール処理
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        // ブラウザのデフォルトの動作を抑制
        e.preventDefault();
        // 後で使用するためにイベントを保存
        deferredPrompt = e;
        // インストールプロンプトを表示
        installPrompt.classList.remove('hidden');
    });

    // インストールボタンのイベントリスナー
    installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) return;
        
        // プロンプトを表示
        deferredPrompt.prompt();
        
        // ユーザーの選択を待つ
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`ユーザーの選択: ${outcome}`);
        
        // イベントを使用したのでリセット
        deferredPrompt = null;
        
        // プロンプトを非表示
        installPrompt.classList.add('hidden');
    });

    // PWAがインストールされたら
    window.addEventListener('appinstalled', () => {
        console.log('PWAがインストールされました');
        installPrompt.classList.add('hidden');
    });
}); 