// ヘルプ機能の実装
document.addEventListener('DOMContentLoaded', () => {
    // ヘルプボタンと関連要素
    const helpBtn = document.getElementById('helpBtn');
    const helpModal = document.getElementById('helpModal');
    const closeHelpBtn = document.getElementById('closeHelpBtn');
    const helpContent = document.getElementById('helpContent');
    
    // ヘルプトピック
    const helpTopics = {
        'basics': {
            title: '基本的な使い方',
            content: `
                <h3>基本的な使い方</h3>
                <p>ホロスコープ計算ツールは、あなたの誕生日時と出生地の情報から占星術のホロスコープを計算するツールです。</p>
                <ol>
                    <li>生年月日を入力します</li>
                    <li>出生時間を入力します</li>
                    <li>出生地の緯度・経度を入力します（「現在地を取得」ボタンで現在の位置を使用することもできます）</li>
                    <li>「計算」ボタンを押して結果を確認します</li>
                </ol>
            `
        },
        'planets': {
            title: '惑星の意味',
            content: `
                <h3>惑星の意味</h3>
                <p>占星術では、各惑星は人格や人生の異なる側面を表します：</p>
                <ul>
                    <li><strong>太陽</strong>：自己の本質、アイデンティティ、目的</li>
                    <li><strong>月</strong>：感情、本能、無意識の反応</li>
                    <li><strong>水星</strong>：思考、コミュニケーション、知性</li>
                    <li><strong>金星</strong>：愛、美、価値観</li>
                    <li><strong>火星</strong>：行動、エネルギー、情熱</li>
                    <li><strong>木星</strong>：拡大、成長、幸運</li>
                    <li><strong>土星</strong>：制限、責任、構造</li>
                    <li><strong>天王星</strong>：変化、革新、独創性</li>
                    <li><strong>海王星</strong>：夢、直感、霊性</li>
                    <li><strong>冥王星</strong>：変容、再生、力</li>
                </ul>
            `
        },
        'signs': {
            title: '星座の意味',
            content: `
                <h3>星座（サイン）の意味</h3>
                <p>12の星座は、惑星がどのように表現されるかを示します：</p>
                <ul>
                    <li><strong>牡羊座</strong>：先駆者、開拓者、行動力</li>
                    <li><strong>牡牛座</strong>：安定、忍耐、実用性</li>
                    <li><strong>双子座</strong>：適応性、コミュニケーション、多様性</li>
                    <li><strong>蟹座</strong>：感受性、保護、感情</li>
                    <li><strong>獅子座</strong>：創造性、自己表現、威厳</li>
                    <li><strong>乙女座</strong>：分析、完璧主義、奉仕</li>
                    <li><strong>天秤座</strong>：バランス、調和、関係性</li>
                    <li><strong>蠍座</strong>：変容、情熱、探究心</li>
                    <li><strong>射手座</strong>：冒険、楽観主義、自由</li>
                    <li><strong>山羊座</strong>：野心、規律、責任</li>
                    <li><strong>水瓶座</strong>：革新、独立、人道主義</li>
                    <li><strong>魚座</strong>：共感、直感、精神性</li>
                </ul>
            `
        },
        'houses': {
            title: 'ハウスの意味',
            content: `
                <h3>ハウス（室）の意味</h3>
                <p>12のハウスは、惑星の影響が人生のどの領域で現れるかを示します：</p>
                <ul>
                    <li><strong>1ハウス</strong>：自己、外見、アイデンティティ</li>
                    <li><strong>2ハウス</strong>：所有物、価値観、収入</li>
                    <li><strong>3ハウス</strong>：コミュニケーション、短距離の旅行、兄弟姉妹</li>
                    <li><strong>4ハウス</strong>：家、家族、ルーツ</li>
                    <li><strong>5ハウス</strong>：創造性、自己表現、楽しみ</li>
                    <li><strong>6ハウス</strong>：健康、日常業務、サービス</li>
                    <li><strong>7ハウス</strong>：パートナーシップ、結婚、開かれた敵</li>
                    <li><strong>8ハウス</strong>：変容、共有資源、性</li>
                    <li><strong>9ハウス</strong>：高等教育、長距離の旅行、哲学</li>
                    <li><strong>10ハウス</strong>：キャリア、社会的地位、権威</li>
                    <li><strong>11ハウス</strong>：友情、グループ、目標</li>
                    <li><strong>12ハウス</strong>：潜在意識、霊性、隠れた敵</li>
                </ul>
            `
        },
        'aspects': {
            title: 'アスペクト',
            content: `
                <h3>アスペクト（角度関係）</h3>
                <p>アスペクトは、ホロスコープ内の惑星間の角度関係を表します：</p>
                <ul>
                    <li><strong>コンジャンクション（合）</strong>：0度。エネルギーの融合、強化。</li>
                    <li><strong>セクスタイル（六分）</strong>：60度。調和、機会、流れ。</li>
                    <li><strong>スクエア（四分）</strong>：90度。緊張、挑戦、行動の必要性。</li>
                    <li><strong>トライン（三分）</strong>：120度。調和、才能、自然な流れ。</li>
                    <li><strong>オポジション（対向）</strong>：180度。対立、バランス、関係性。</li>
                </ul>
            `
        },
        'offline': {
            title: 'オフライン機能',
            content: `
                <h3>オフライン機能</h3>
                <p>このアプリはPWA（Progressive Web App）として実装されているため、次のオフライン機能があります：</p>
                <ul>
                    <li>インターネット接続がなくてもアプリにアクセスできます</li>
                    <li>過去の計算結果はローカルストレージに保存され、オフラインでも表示できます</li>
                    <li>「インストール」ボタンを使って、デスクトップやホーム画面にアプリを追加できます</li>
                </ul>
                <p>インターネット接続がある時に新しい計算を行うと、その結果も保存され、オフラインでアクセスできるようになります。</p>
            `
        }
    };

    // ヘルプモーダルを開く
    helpBtn.addEventListener('click', () => {
        // デフォルトでは「基本的な使い方」を表示
        showHelpTopic('basics');
        helpModal.classList.remove('hidden');
    });

    // ヘルプモーダルを閉じる
    closeHelpBtn.addEventListener('click', () => {
        helpModal.classList.add('hidden');
    });

    // ESCキーでモーダルを閉じる
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !helpModal.classList.contains('hidden')) {
            helpModal.classList.add('hidden');
        }
    });

    // モーダル外をクリックした時に閉じる
    helpModal.addEventListener('click', (e) => {
        if (e.target === helpModal) {
            helpModal.classList.add('hidden');
        }
    });

    // トピックリンクのイベントリスナーを設定
    document.querySelectorAll('.help-topic-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const topic = e.target.getAttribute('data-topic');
            showHelpTopic(topic);
        });
    });

    // ヘルプトピックを表示する関数
    function showHelpTopic(topic) {
        if (helpTopics[topic]) {
            const helpData = helpTopics[topic];
            helpContent.innerHTML = helpData.content;
            
            // 現在選択されているトピックをハイライト
            document.querySelectorAll('.help-topic-link').forEach(link => {
                if (link.getAttribute('data-topic') === topic) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }
    }
}); 