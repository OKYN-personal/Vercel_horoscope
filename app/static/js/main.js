document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('horoscopeForm');
    const errorDiv = document.getElementById('errorDisplay');
    
    form.addEventListener('submit', function(e) {
        // e.preventDefault(); // これを削除し、通常のフォーム送信を行う
        
        // エラー表示をクリアする (送信前に)
        if (errorDiv) {
             errorDiv.classList.add('hidden');
             errorDiv.innerHTML = '';
        }
        
        // ローディング表示なども不要になるため削除
        // resultDiv.innerHTML = '<div class="loading">計算中...</div>';
        // resultDiv.classList.remove('hidden');
        
        // fetch APIを使った非同期通信部分はすべて削除
        /*
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/calculate', {
                method: 'POST',
                body: formData
            });
            
            // response.json() を期待していたが、HTMLが返ってくるためエラーになる
            const data = await response.json(); 
            
            if (data.success) {
                // displayResults 関数も不要になる
                // displayResults(data.result, data.pdf_url); 
                // resultDiv.classList.remove('hidden');
            } else {
                errorDiv.innerHTML = `エラー: ${data.error || '不明なエラー'}`;
                errorDiv.classList.remove('hidden');
                // resultDiv.innerHTML = ''; 
                // resultDiv.classList.add('hidden');
            }
        } catch (error) {
            // Unexpected token '<' エラーはここで捕捉される可能性が高い
            errorDiv.innerHTML = `エラーが発生しました: ${error.message}`;
            errorDiv.classList.remove('hidden');
            // resultDiv.innerHTML = ''; 
            // resultDiv.classList.add('hidden');
        }
        */
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