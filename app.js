// TranslateGemma 음성 번역 앱
class TranslateGemmaApp {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.apiKey = localStorage.getItem('hf_api_key') || '';

        // 번역 기록 저장
        this.translationHistory = [];

        // 무음 타이머 (10초)
        this.silenceTimeout = null;
        this.silenceCountdown = null;
        this.lastSpeechTime = null;
        this.SILENCE_LIMIT = 10; // 초

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
            // continuous 모드에서 자동 재시작 (사용자가 중지하지 않은 경우)
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
            // 음성 감지됨 - 타이머 리셋
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

            // 현재 텍스트 표시
            const currentText = finalTranscript || interimTranscript;
            if (currentText) {
                this.displaySourceText(currentText, !event.results[event.results.length - 1].isFinal);
            }

            // 최종 결과면 번역 실행
            if (finalTranscript && finalTranscript.trim()) {
                this.translateText(finalTranscript.trim());
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);

            if (event.error === 'no-speech') {
                // 무음 - 타이머 계속
                return;
            }

            let errorMsg = '음성 인식 오류가 발생했습니다.';
            switch (event.error) {
                case 'audio-capture':
                    errorMsg = '마이크를 찾을 수 없습니다.';
                    break;
                case 'not-allowed':
                    errorMsg = '마이크 권한이 거부되었습니다.';
                    break;
                case 'network':
                    errorMsg = '네트워크 오류가 발생했습니다.';
                    break;
            }

            this.showStatus(errorMsg, 'error');
        };
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

    initEventListeners() {
        // 시작/중지 버튼
        this.micBtn.addEventListener('click', () => this.toggleListening());

        // 저장 버튼
        this.saveBtn.addEventListener('click', () => this.saveTranslation());

        // 지우기 버튼
        this.clearAllBtn.addEventListener('click', () => this.clearAll());

        // 언어 선택 변경
        this.sourceLang.addEventListener('change', () => {
            this.updateLabels();
            this.updateRecognitionLanguage();
            this.saveSettings();
        });

        this.targetLang.addEventListener('change', () => {
            this.updateLabels();
            this.saveSettings();
        });

        // 언어 교환
        this.swapBtn.addEventListener('click', () => this.swapLanguages());

        // API 키 저장
        this.apiKeyInput.addEventListener('change', () => {
            this.apiKey = this.apiKeyInput.value;
            localStorage.setItem('hf_api_key', this.apiKey);
            this.showStatus('API 키가 저장되었습니다.', 'success');
            setTimeout(() => this.hideStatus(), 2000);
        });

        // 키보드 단축키
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

        const langNames = {
            ko: 'Korean', en: 'English', ja: 'Japanese', zh: 'Chinese',
            es: 'Spanish', fr: 'French', de: 'German', pt: 'Portuguese',
            ru: 'Russian', ar: 'Arabic', hi: 'Hindi', vi: 'Vietnamese',
            th: 'Thai', id: 'Indonesian'
        };

        const sourceLangName = langNames[this.sourceLang.value];
        const targetLangName = langNames[this.targetLang.value];

        try {
            let translation = await this.callTranslationAPI(text, sourceLangName, targetLangName);

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

    async callTranslationAPI(text, sourceLang, targetLang) {
        // 여러 모델 시도
        const models = [
            'google/gemma-3-4b-it',
            'google/gemma-2-2b-it',
            'mistralai/Mistral-7B-Instruct-v0.3'
        ];

        const prompt = `Translate the following text from ${sourceLang} to ${targetLang}. Only output the translation, nothing else.

Text: ${text}

Translation:`;

        for (const model of models) {
            try {
                const response = await fetch(
                    `https://api-inference.huggingface.co/models/${model}`,
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${this.apiKey}`,
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            inputs: prompt,
                            parameters: {
                                max_new_tokens: 256,
                                temperature: 0.3,
                                do_sample: true,
                                return_full_text: false
                            }
                        })
                    }
                );

                if (response.status === 503) {
                    // 모델 로딩 중 - 다음 모델 시도
                    console.log(`Model ${model} is loading, trying next...`);
                    continue;
                }

                if (response.status === 401) {
                    throw new Error('API 키가 유효하지 않습니다.');
                }

                if (!response.ok) {
                    continue;
                }

                const data = await response.json();
                let translation = '';

                if (Array.isArray(data) && data[0]?.generated_text) {
                    translation = data[0].generated_text;
                } else if (data.generated_text) {
                    translation = data.generated_text;
                } else if (Array.isArray(data) && typeof data[0] === 'string') {
                    translation = data[0];
                }

                if (translation) {
                    // 불필요한 부분 정리
                    translation = translation
                        .replace(/^Translation:\s*/i, '')
                        .replace(/<[^>]*>/g, '')
                        .split('\n')[0]
                        .trim();

                    if (translation && translation !== text) {
                        return translation;
                    }
                }
            } catch (e) {
                console.error(`Error with model ${model}:`, e);
                if (e.message.includes('API 키')) {
                    throw e;
                }
            }
        }

        throw new Error('번역 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.');
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
