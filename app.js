// TranslateGemma 음성 번역 앱
class TranslateGemmaApp {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.apiKey = localStorage.getItem('hf_api_key') || '';
        this.apiConnected = false;

        // 번역 기록 저장
        this.translationHistory = [];

        // 무음 타이머 (10초)
        this.silenceCountdown = null;
        this.lastSpeechTime = null;
        this.SILENCE_LIMIT = 10;

        // Helsinki-NLP 번역 모델 매핑
        this.translationModels = {
            'ko-en': 'Helsinki-NLP/opus-mt-ko-en',
            'en-ko': 'Helsinki-NLP/opus-mt-en-ko',
            'ja-en': 'Helsinki-NLP/opus-mt-ja-en',
            'en-ja': 'Helsinki-NLP/opus-mt-en-jap',
            'zh-en': 'Helsinki-NLP/opus-mt-zh-en',
            'en-zh': 'Helsinki-NLP/opus-mt-en-zh',
            'es-en': 'Helsinki-NLP/opus-mt-es-en',
            'en-es': 'Helsinki-NLP/opus-mt-en-es',
            'fr-en': 'Helsinki-NLP/opus-mt-fr-en',
            'en-fr': 'Helsinki-NLP/opus-mt-en-fr',
            'de-en': 'Helsinki-NLP/opus-mt-de-en',
            'en-de': 'Helsinki-NLP/opus-mt-en-de',
            'ru-en': 'Helsinki-NLP/opus-mt-ru-en',
            'en-ru': 'Helsinki-NLP/opus-mt-en-ru',
            'pt-en': 'Helsinki-NLP/opus-mt-mul-en',
            'en-pt': 'Helsinki-NLP/opus-mt-en-roa',
            'ar-en': 'Helsinki-NLP/opus-mt-ar-en',
            'en-ar': 'Helsinki-NLP/opus-mt-en-ar',
            'vi-en': 'Helsinki-NLP/opus-mt-vi-en',
            'en-vi': 'Helsinki-NLP/opus-mt-en-vi',
            'th-en': 'Helsinki-NLP/opus-mt-th-en',
            'en-th': 'Helsinki-NLP/opus-mt-en-mul',
            'id-en': 'Helsinki-NLP/opus-mt-id-en',
            'en-id': 'Helsinki-NLP/opus-mt-en-id',
            'hi-en': 'Helsinki-NLP/opus-mt-hi-en',
            'en-hi': 'Helsinki-NLP/opus-mt-en-hi'
        };

        this.initElements();
        this.initSpeechRecognition();
        this.initEventListeners();
        this.loadSettings();
    }

    initElements() {
        this.micBtn = document.getElementById('micBtn');
        this.saveBtn = document.getElementById('saveBtn');
        this.clearAllBtn = document.getElementById('clearAllBtn');
        this.sourceText = document.getElementById('sourceText');
        this.targetText = document.getElementById('targetText');
        this.sourceLang = document.getElementById('sourceLang');
        this.targetLang = document.getElementById('targetLang');
        this.sourceLabel = document.getElementById('sourceLabel');
        this.targetLabel = document.getElementById('targetLabel');
        this.apiKeyInput = document.getElementById('apiKey');
        this.swapBtn = document.getElementById('swapLang');
        this.status = document.getElementById('status');
        this.silenceTimer = document.getElementById('silenceTimer');
        this.apiStatus = document.getElementById('apiStatus');
        this.testApiBtn = document.getElementById('testApiBtn');
        this.apiMessage = document.getElementById('apiMessage');
    }

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            this.showStatus('이 브라우저는 음성 인식을 지원하지 않습니다. Chrome 브라우저를 사용해주세요.', 'error');
            this.micBtn.disabled = true;
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;

        this.recognition.onstart = () => {
            this.isListening = true;
            this.lastSpeechTime = Date.now();
            this.micBtn.classList.add('listening');
            this.updateMicButton(true);
            this.showStatus('음성을 듣고 있습니다... (10초 무음시 자동 중지)', 'info');
            this.startSilenceTimer();
        };

        this.recognition.onend = () => {
            if (this.isListening) {
                try {
                    this.recognition.start();
                } catch (e) {
                    this.stopListening();
                }
            } else {
                this.stopListening();
            }
        };

        this.recognition.onresult = (event) => {
            this.lastSpeechTime = Date.now();
            this.resetSilenceTimer();

            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            const currentText = finalTranscript || interimTranscript;
            if (currentText) {
                this.displaySourceText(currentText, !event.results[event.results.length - 1].isFinal);
            }

            if (finalTranscript && finalTranscript.trim()) {
                this.translateText(finalTranscript.trim());
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'no-speech') return;

            let errorMsg = '음성 인식 오류가 발생했습니다.';
            switch (event.error) {
                case 'audio-capture':
                    errorMsg = '마이크를 찾을 수 없습니다.';
                    break;
                case 'not-allowed':
                    errorMsg = '마이크 권한이 거부되었습니다.';
                    break;
            }
            this.showStatus(errorMsg, 'error');
        };
    }

    initEventListeners() {
        this.micBtn.addEventListener('click', () => this.toggleListening());
        this.saveBtn.addEventListener('click', () => this.saveTranslation());
        this.clearAllBtn.addEventListener('click', () => this.clearAll());
        this.testApiBtn.addEventListener('click', () => this.testApiConnection());

        this.sourceLang.addEventListener('change', () => {
            this.updateLabels();
            this.updateRecognitionLanguage();
            this.saveSettings();
        });

        this.targetLang.addEventListener('change', () => {
            this.updateLabels();
            this.saveSettings();
        });

        this.swapBtn.addEventListener('click', () => this.swapLanguages());

        this.apiKeyInput.addEventListener('input', () => {
            this.apiKey = this.apiKeyInput.value;
            localStorage.setItem('hf_api_key', this.apiKey);
            // API 키 변경시 연결 상태 초기화
            this.setApiStatus('disconnected');
            this.apiConnected = false;
        });

        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && e.ctrlKey) {
                e.preventDefault();
                this.toggleListening();
            }
            if (e.code === 'KeyS' && e.ctrlKey) {
                e.preventDefault();
                this.saveTranslation();
            }
        });
    }

    loadSettings() {
        if (this.apiKey) {
            this.apiKeyInput.value = this.apiKey;
            // 저장된 API 키가 있으면 자동 테스트
            this.testApiConnection();
        } else {
            this.setApiStatus('disconnected');
        }

        const savedSourceLang = localStorage.getItem('sourceLang');
        const savedTargetLang = localStorage.getItem('targetLang');

        if (savedSourceLang) this.sourceLang.value = savedSourceLang;
        if (savedTargetLang) this.targetLang.value = savedTargetLang;

        this.updateLabels();
        this.updateRecognitionLanguage();
    }

    saveSettings() {
        localStorage.setItem('sourceLang', this.sourceLang.value);
        localStorage.setItem('targetLang', this.targetLang.value);
    }

    setApiStatus(status) {
        this.apiStatus.className = 'api-status ' + status;

        switch (status) {
            case 'disconnected':
                this.apiStatus.title = 'API 미연결';
                break;
            case 'checking':
                this.apiStatus.title = 'API 확인 중...';
                break;
            case 'connected':
                this.apiStatus.title = 'API 연결됨';
                break;
        }
    }

    async testApiConnection() {
        if (!this.apiKey || !this.apiKey.startsWith('hf_')) {
            this.setApiStatus('disconnected');
            this.apiMessage.textContent = 'API 키를 입력해주세요 (hf_로 시작)';
            this.apiMessage.className = 'api-message error';
            this.apiConnected = false;
            return;
        }

        this.setApiStatus('checking');
        this.apiMessage.textContent = '연결 테스트 중... (최대 30초 소요)';
        this.apiMessage.className = 'api-message checking';
        this.testApiBtn.disabled = true;

        // 30초 타임아웃 설정
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        try {
            const response = await fetch(
                'https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-ko',
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        inputs: 'Hello',
                        options: {
                            wait_for_model: true
                        }
                    }),
                    signal: controller.signal
                }
            );

            clearTimeout(timeoutId);

            if (response.status === 401) {
                throw new Error('API 키가 유효하지 않습니다. 권한을 확인하세요.');
            }

            if (response.status === 403) {
                throw new Error('API 접근 권한이 없습니다. Inference 권한을 확인하세요.');
            }

            if (response.status === 503) {
                // 모델 로딩 중이지만 API 키는 유효
                this.setApiStatus('connected');
                this.apiMessage.textContent = '연결 성공! (모델 로딩 중, 잠시 후 번역 가능)';
                this.apiMessage.className = 'api-message success';
                this.apiConnected = true;
                return;
            }

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 100)}`);
            }

            const data = await response.json();

            if (data && (data[0]?.translation_text || data.error?.includes('loading'))) {
                this.setApiStatus('connected');
                this.apiMessage.textContent = '연결 성공! 번역 준비 완료';
                this.apiMessage.className = 'api-message success';
                this.apiConnected = true;
            } else if (Array.isArray(data)) {
                this.setApiStatus('connected');
                this.apiMessage.textContent = '연결 성공!';
                this.apiMessage.className = 'api-message success';
                this.apiConnected = true;
            } else {
                throw new Error('응답 형식 오류');
            }

        } catch (error) {
            clearTimeout(timeoutId);
            console.error('API test error:', error);
            this.setApiStatus('disconnected');

            if (error.name === 'AbortError') {
                this.apiMessage.textContent = '연결 시간 초과. 네트워크를 확인하세요.';
            } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                this.apiMessage.textContent = '네트워크 오류. 인터넷 연결을 확인하세요.';
            } else {
                this.apiMessage.textContent = error.message;
            }

            this.apiMessage.className = 'api-message error';
            this.apiConnected = false;
        } finally {
            this.testApiBtn.disabled = false;
        }
    }

    updateLabels() {
        const langNames = {
            ko: '한국어', en: 'English', ja: '日本語', zh: '中文',
            es: 'Español', fr: 'Français', de: 'Deutsch', pt: 'Português',
            ru: 'Русский', ar: 'العربية', hi: 'हिन्दी', vi: 'Tiếng Việt',
            th: 'ไทย', id: 'Bahasa Indonesia'
        };

        this.sourceLabel.textContent = `${langNames[this.sourceLang.value]} (음성 입력)`;
        this.targetLabel.textContent = `${langNames[this.targetLang.value]} (번역)`;
    }

    updateRecognitionLanguage() {
        if (this.recognition) {
            const langCodes = {
                ko: 'ko-KR', en: 'en-US', ja: 'ja-JP', zh: 'zh-CN',
                es: 'es-ES', fr: 'fr-FR', de: 'de-DE', pt: 'pt-BR',
                ru: 'ru-RU', ar: 'ar-SA', hi: 'hi-IN', vi: 'vi-VN',
                th: 'th-TH', id: 'id-ID'
            };
            this.recognition.lang = langCodes[this.sourceLang.value] || 'en-US';
        }
    }

    toggleListening() {
        if (!this.apiConnected) {
            this.showStatus('먼저 API 연결을 확인해주세요. [연결 테스트] 버튼을 클릭하세요.', 'warning');
            return;
        }

        if (this.isListening) {
            this.stopListening();
            this.showStatus('음성 인식이 중지되었습니다.', 'info');
            setTimeout(() => this.hideStatus(), 2000);
        } else {
            this.updateRecognitionLanguage();
            try {
                this.recognition.start();
            } catch (e) {
                this.showStatus('음성 인식을 시작할 수 없습니다.', 'error');
            }
        }
    }

    startSilenceTimer() {
        this.clearSilenceTimers();

        this.silenceCountdown = setInterval(() => {
            if (!this.isListening) {
                this.clearSilenceTimers();
                return;
            }

            const elapsed = Math.floor((Date.now() - this.lastSpeechTime) / 1000);
            const remaining = this.SILENCE_LIMIT - elapsed;

            if (remaining <= 5 && remaining > 0) {
                this.silenceTimer.textContent = `무음 ${remaining}초 후 자동 중지...`;
                this.silenceTimer.classList.add('warning');
            } else if (remaining > 5) {
                this.silenceTimer.textContent = '';
                this.silenceTimer.classList.remove('warning');
            }

            if (remaining <= 0) {
                this.showStatus('10초 무음으로 자동 중지되었습니다.', 'warning');
                this.stopListening();
            }
        }, 1000);
    }

    resetSilenceTimer() {
        this.lastSpeechTime = Date.now();
        this.silenceTimer.textContent = '';
        this.silenceTimer.classList.remove('warning');
    }

    clearSilenceTimers() {
        if (this.silenceCountdown) {
            clearInterval(this.silenceCountdown);
            this.silenceCountdown = null;
        }
        this.silenceTimer.textContent = '';
        this.silenceTimer.classList.remove('warning');
    }

    updateMicButton(listening) {
        if (listening) {
            this.micBtn.innerHTML = `
                <svg class="mic-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                <span>중지</span>
                <div class="listening-indicator">
                    <span></span><span></span><span></span><span></span>
                </div>
            `;
        } else {
            this.micBtn.innerHTML = `
                <svg class="mic-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                <span>시작</span>
            `;
        }
    }

    stopListening() {
        this.isListening = false;
        this.micBtn.classList.remove('listening');
        this.updateMicButton(false);
        this.clearSilenceTimers();

        try {
            this.recognition.stop();
        } catch (e) {}

        this.hideStatus();
    }

    swapLanguages() {
        const temp = this.sourceLang.value;
        this.sourceLang.value = this.targetLang.value;
        this.targetLang.value = temp;

        this.updateLabels();
        this.updateRecognitionLanguage();
        this.saveSettings();
    }

    displaySourceText(currentText, isInterim = false) {
        let html = '';

        this.translationHistory.forEach(item => {
            html += `<p class="history-item">${item.source}</p>`;
        });

        if (currentText) {
            html += `<p class="${isInterim ? 'interim' : 'current'}">${currentText}</p>`;
        }

        this.sourceText.innerHTML = html || '<p class="placeholder">시작 버튼을 눌러 말하세요...</p>';
        this.sourceText.scrollTop = this.sourceText.scrollHeight;
    }

    displayTargetText() {
        let html = '';

        this.translationHistory.forEach(item => {
            html += `<p class="history-item">${item.target}</p>`;
        });

        this.targetText.innerHTML = html || '<p class="placeholder">번역 결과가 여기에 표시됩니다...</p>';
        this.targetText.scrollTop = this.targetText.scrollHeight;
    }

    async translateText(text) {
        if (!this.apiKey) {
            this.showStatus('API 키를 입력해주세요.', 'warning');
            return;
        }

        // 번역 중 표시
        let tempHtml = '';
        this.translationHistory.forEach(item => {
            tempHtml += `<p class="history-item">${item.target}</p>`;
        });
        tempHtml += '<p class="translating">번역 중...<span class="loading"></span></p>';
        this.targetText.innerHTML = tempHtml;
        this.targetText.scrollTop = this.targetText.scrollHeight;

        try {
            const translation = await this.callTranslationAPI(text);

            if (translation) {
                this.translationHistory.push({
                    source: text,
                    target: translation,
                    timestamp: new Date().toISOString()
                });

                this.displaySourceText('');
                this.displayTargetText();
            }

        } catch (error) {
            console.error('Translation error:', error);
            this.showStatus(`번역 오류: ${error.message}`, 'error');
            this.displayTargetText();
        }
    }

    async callTranslationAPI(text) {
        const sourceLang = this.sourceLang.value;
        const targetLang = this.targetLang.value;

        // 직접 번역 모델 찾기
        let modelKey = `${sourceLang}-${targetLang}`;
        let model = this.translationModels[modelKey];

        // 직접 모델이 없으면 영어를 거쳐 번역
        let needsPivot = false;
        if (!model && sourceLang !== 'en' && targetLang !== 'en') {
            needsPivot = true;
        }

        if (needsPivot) {
            // 소스 → 영어 → 타겟 (피벗 번역)
            const toEnglish = await this.translateWithModel(text, `${sourceLang}-en`);
            if (toEnglish) {
                const toTarget = await this.translateWithModel(toEnglish, `en-${targetLang}`);
                return toTarget;
            }
            throw new Error('번역 실패');
        } else {
            return await this.translateWithModel(text, modelKey);
        }
    }

    async translateWithModel(text, langPair) {
        let model = this.translationModels[langPair];

        // 모델이 없으면 다국어 모델 사용
        if (!model) {
            if (langPair.endsWith('-en')) {
                model = 'Helsinki-NLP/opus-mt-mul-en';
            } else if (langPair.startsWith('en-')) {
                model = 'Helsinki-NLP/opus-mt-en-mul';
            } else {
                throw new Error(`지원하지 않는 언어 조합: ${langPair}`);
            }
        }

        const response = await fetch(
            `https://api-inference.huggingface.co/models/${model}`,
            {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    inputs: text,
                    options: {
                        wait_for_model: true
                    }
                })
            }
        );

        if (response.status === 401) {
            this.setApiStatus('disconnected');
            this.apiConnected = false;
            throw new Error('API 키가 유효하지 않습니다.');
        }

        if (response.status === 503) {
            const errorData = await response.json();
            if (errorData.estimated_time) {
                throw new Error(`모델 로딩 중... ${Math.ceil(errorData.estimated_time)}초 후 다시 시도해주세요.`);
            }
            throw new Error('모델 로딩 중입니다. 잠시 후 다시 시도해주세요.');
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status} 오류`);
        }

        const data = await response.json();

        if (Array.isArray(data) && data[0]?.translation_text) {
            return data[0].translation_text;
        } else if (data.translation_text) {
            return data.translation_text;
        } else if (Array.isArray(data) && typeof data[0] === 'string') {
            return data[0];
        }

        throw new Error('번역 응답 형식 오류');
    }

    clearAll() {
        this.translationHistory = [];

        this.sourceText.innerHTML = '<p class="placeholder">시작 버튼을 눌러 말하세요...</p>';
        this.targetText.innerHTML = '<p class="placeholder">번역 결과가 여기에 표시됩니다...</p>';

        this.showStatus('모든 내용이 지워졌습니다.', 'success');
        setTimeout(() => this.hideStatus(), 2000);
    }

    saveTranslation() {
        if (this.translationHistory.length === 0) {
            this.showStatus('저장할 번역 내용이 없습니다.', 'warning');
            return;
        }

        const langNames = {
            ko: '한국어', en: 'English', ja: '日本語', zh: '中文',
            es: 'Español', fr: 'Français', de: 'Deutsch', pt: 'Português',
            ru: 'Русский', ar: 'العربية', hi: 'हिन्दी', vi: 'Tiếng Việt',
            th: 'ไทย', id: 'Bahasa Indonesia'
        };

        let content = `TranslateGemma 번역 결과\n`;
        content += `${'='.repeat(50)}\n`;
        content += `날짜: ${new Date().toLocaleString('ko-KR')}\n`;
        content += `번역 방향: ${langNames[this.sourceLang.value]} → ${langNames[this.targetLang.value]}\n`;
        content += `${'='.repeat(50)}\n\n`;

        this.translationHistory.forEach((item, index) => {
            content += `[${index + 1}]\n`;
            content += `원문: ${item.source}\n`;
            content += `번역: ${item.target}\n\n`;
        });

        content += `${'='.repeat(50)}\n`;
        content += `총 ${this.translationHistory.length}개 문장 번역됨\n`;

        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        const now = new Date();
        const filename = `translation_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.txt`;

        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showStatus(`${filename} 저장 완료!`, 'success');
        setTimeout(() => this.hideStatus(), 3000);
    }

    showStatus(message, type) {
        this.status.textContent = message;
        this.status.className = `status show ${type}`;
    }

    hideStatus() {
        this.status.classList.remove('show');
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    new TranslateGemmaApp();
});
