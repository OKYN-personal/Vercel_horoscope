document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('horoscopeForm');
    const resultContainer = document.getElementById('resultContainer');
    const resultElement = document.getElementById('result');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const offlineIndicator = document.getElementById('offlineIndicator');
    
    // オフライン状態の検出
    function updateOnlineStatus() {
        if (navigator.onLine) {
            offlineIndicator.classList.add('hidden');
        } else {
            offlineIndicator.classList.remove('hidden');
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus(); // 初期状態を確認
    
    // APIサーバーのウォームアップを実行（コールドスタート対策）
    warmupApiServer();
    
    // 現在の日付をデフォルト値として設定
    const today = new Date();
    const formattedDate = today.toISOString().split('T')[0];
    document.getElementById('birthDate').value = formattedDate;
    
    // 位置情報の取得（対応ブラウザのみ）
    if ('geolocation' in navigator) {
        const geoButton = document.createElement('button');
        geoButton.type = 'button';
        geoButton.textContent = '現在地を使用';
        geoButton.className = 'geo-button';
        geoButton.onclick = function() {
            geoButton.textContent = '取得中...';
            geoButton.disabled = true;
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    document.getElementById('latitude').value = position.coords.latitude;
                    document.getElementById('longitude').value = position.coords.longitude;
                    geoButton.textContent = '位置情報を取得しました';
                    setTimeout(() => {
                        geoButton.textContent = '現在地を使用';
                        geoButton.disabled = false;
                    }, 3000);
                },
                function(error) {
                    console.error('位置情報の取得に失敗:', error);
                    geoButton.textContent = '位置情報の取得に失敗';
                    geoButton.disabled = false;
                },
                { enableHighAccuracy: true }
            );
        };
        
        // 緯度の入力欄の後に挿入
        const latitudeGroup = document.getElementById('latitude').parentNode;
        latitudeGroup.appendChild(geoButton);
    }
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // オフライン時は計算不可
        if (!navigator.onLine) {
            alert('オフラインモードではホロスコープ計算ができません。インターネット接続を確認してください。');
            return;
        }
        
        // 入力値の取得
        const birthDate = document.getElementById('birthDate').value;
        const birthTime = document.getElementById('birthTime').value;
        const latitude = document.getElementById('latitude').value;
        const longitude = document.getElementById('longitude').value;
        
        // 入力値のバリデーション
        if (!birthDate || !birthTime || !latitude || !longitude) {
            alert('すべての項目を入力してください');
            return;
        }
        
        // ローディング表示
        resultContainer.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        loadingIndicator.innerHTML = '<p>計算中...<br>初回アクセス時は少々時間がかかる場合があります（15-30秒）</p>';
        
        try {
            // タイムアウト処理の追加（コールドスタート対策）
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60秒でタイムアウト
            
            // APIリクエスト
            let response;
            try {
                response = await fetch('/calculate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        birth_date: birthDate,
                        birth_time: birthTime,
                        latitude: parseFloat(latitude),
                        longitude: parseFloat(longitude)
                    }),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
            } catch (fetchError) {
                if (fetchError.name === 'AbortError') {
                    throw new Error('計算に時間がかかりすぎています。後でもう一度お試しください。');
                }
                throw fetchError;
            }
            
            if (!response.ok) {
                throw new Error('計算中にエラーが発生しました');
            }
            
            const data = await response.json();
            
            // 結果をローカルストレージに保存（オフライン閲覧用）
            try {
                const lastResult = {
                    timestamp: new Date().toISOString(),
                    params: {
                        birth_date: birthDate,
                        birth_time: birthTime,
                        latitude: parseFloat(latitude),
                        longitude: parseFloat(longitude)
                    },
                    data: data
                };
                localStorage.setItem('lastHoroscopeResult', JSON.stringify(lastResult));
            } catch (e) {
                console.warn('結果のキャッシュに失敗:', e);
            }
            
            // 結果の表示
            displayResult(data);
            
            // ローディング非表示
            loadingIndicator.classList.add('hidden');
            resultContainer.classList.remove('hidden');
            
        } catch (error) {
            console.error('Error:', error);
            alert(error.message || 'エラーが発生しました。もう一度お試しください。');
            loadingIndicator.classList.add('hidden');
            
            // オフライン時はキャッシュした結果があれば表示
            if (!navigator.onLine) {
                try {
                    const lastResult = JSON.parse(localStorage.getItem('lastHoroscopeResult'));
                    if (lastResult) {
                        alert('オフラインモードのため、前回の計算結果を表示します');
                        displayResult(lastResult.data);
                        resultContainer.classList.remove('hidden');
                    }
                } catch (e) {
                    console.error('キャッシュ結果の読み込みに失敗:', e);
                }
            }
        }
    });
    
    // APIサーバーをウォームアップする関数
    async function warmupApiServer() {
        try {
            // 環境によってはCORSエラーになるため、フロントエンドのプロキシを経由
            const response = await fetch('/warmup', { method: 'GET' });
            console.log('API server warmed up:', await response.text());
        } catch (error) {
            console.log('API warmup failed, will retry on calculation');
        }
    }
    
    // 結果表示関数
    function displayResult(data) {
        // 惑星の名前（日本語）
        const planetNames = [
            '太陽', '月', '水星', '金星', '火星', 
            '木星', '土星', '天王星', '海王星', '冥王星'
        ];
        
        // 黄道十二宮（サイン）の名前
        const signNames = [
            '牡羊座', '牡牛座', '双子座', '蟹座', '獅子座', 
            '乙女座', '天秤座', '蠍座', '射手座', '山羊座', 
            '水瓶座', '魚座'
        ];
        
        // テーブル形式で表示
        let resultHtml = '<h3>惑星位置</h3>';
        resultHtml += '<table border="1" cellpadding="5" cellspacing="0">';
        resultHtml += '<tr><th>惑星</th><th>サイン</th><th>度数</th></tr>';
        
        // 惑星情報を表示
        for (let i = 0; i < 10; i++) {
            const position = data.planets[i];
            const sign = Math.floor(position / 30);
            const degree = position % 30;
            
            resultHtml += `<tr>
                <td>${planetNames[i]}</td>
                <td>${signNames[sign]}</td>
                <td>${degree.toFixed(2)}°</td>
            </tr>`;
        }
        
        resultHtml += '</table>';
        
        // ハウス情報
        resultHtml += '<h3>ハウス</h3>';
        resultHtml += '<table border="1" cellpadding="5" cellspacing="0">';
        resultHtml += '<tr><th>ハウス</th><th>度数</th></tr>';
        
        for (let i = 0; i < 12; i++) {
            resultHtml += `<tr>
                <td>${i+1}ハウス</td>
                <td>${data.houses[i].toFixed(2)}°</td>
            </tr>`;
        }
        
        resultHtml += '</table>';
        
        // 結果要素に表示
        resultElement.innerHTML = resultHtml;
    }
}); 