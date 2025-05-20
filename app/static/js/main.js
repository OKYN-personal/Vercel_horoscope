document.addEventListener('DOMContentLoaded', function() {
    // ナビゲーションバーのトグル機能のサポート
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const targetId = this.getAttribute('data-bs-target');
            if (targetId) {
                const target = document.querySelector(targetId);
                if (target) {
                    target.classList.toggle('show');
                }
            }
        });
    }
    
    const form = document.getElementById('horoscopeForm');
    const errorDiv = document.getElementById('errorDisplay');
    
    // トランジット日時のデフォルト値を現在の日付の12:00に設定
    const transitDateField = document.getElementById('transitDate');
    if (transitDateField) {
        const today = new Date();
        today.setHours(12, 0, 0); // 12:00に設定
        
        // YYYY-MM-DDThh:mm 形式にフォーマット
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        const hours = String(today.getHours()).padStart(2, '0');
        const minutes = String(today.getMinutes()).padStart(2, '0');
        
        const formattedDate = `${year}-${month}-${day}T${hours}:${minutes}`;
        transitDateField.value = formattedDate;
    }
    
    // 緯度経度入力フィールドのトグル機能
    const toggleBtn = document.getElementById('toggleCoordinates');
    const coordinatesFields = document.getElementById('coordinatesFields');
    
    if (toggleBtn && coordinatesFields) {
        toggleBtn.addEventListener('click', function() {
            if (coordinatesFields.style.display === 'none') {
                coordinatesFields.style.display = 'block';
                toggleBtn.textContent = '緯度経度入力を隠す';
            } else {
                coordinatesFields.style.display = 'none';
                toggleBtn.textContent = '緯度経度を手動入力する';
            }
        });
        
        // 緯度経度が入力されたらフィードバックも更新
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        const feedbackEl = document.getElementById('locationFeedback');
        
        function updateCoordinateFeedback() {
            if (latInput.value && lngInput.value) {
                try {
                    const lat = parseFloat(latInput.value);
                    const lng = parseFloat(lngInput.value);
                    feedbackEl.innerHTML = `
                        <span class="coords-badge">緯度: ${lat.toFixed(6)}</span>
                        <span class="coords-badge">経度: ${lng.toFixed(6)}</span>
                        <span>手動入力された座標</span>
                    `;
                    // 手動入力されたときは座標入力フィールドを表示
                    coordinatesFields.style.display = 'block';
                    toggleBtn.textContent = '緯度経度入力を隠す';
                } catch (e) {
                    feedbackEl.textContent = '有効な緯度経度を入力してください';
                }
            }
        }
        
        latInput.addEventListener('change', updateCoordinateFeedback);
        lngInput.addEventListener('change', updateCoordinateFeedback);
    }
    
    form.addEventListener('submit', function(e) {
        // エラー表示をクリアする (送信前に)
        if (errorDiv) {
             errorDiv.classList.add('hidden');
             errorDiv.innerHTML = '';
        }
    });
});

// displayResults 関数全体も不要になるため削除
/*
function displayResults(resultData, pdfUrl) {
    const resultDiv = document.getElementById('result');
    
    // 結果のHTML生成 (resultData を使用)
    let html = `...`; // (省略)
    
    resultDiv.innerHTML = html;
}
*/ 