// TranslateGemma 음성 번역 앱
class TranslateGemmaApp {
    constructor() {
        this.isListening = false;
        this.recognition = null;
        this.apiKey = localStorage.getItem('hf_api_key') || '';

        // 번역 기록 저장
        this.translationHistory = [];
        this.currentSourceText = '';

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
            this.micBtn.classList.add('listening');
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
            this.showStatus('음성을 듣고 있습니다... (실시간 번역 중)', 'info');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.micBtn.classList.remove('listening');
            this.micBtn.innerHTML = `
                <svg class="mic-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                <span>시작</span>
            `;
            this.hideStatus();
        };

        this.recognition.onresult = (event) => {
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

            // 현재 텍스트 표시 (기존 기록 + 현재 입력)
            const currentText = finalTranscript || interimTranscript;
            if (currentText) {
                this.displaySourceText(currentText, !event.results[event.results.length - 1].isFinal);
            }

            // 최종 결과면 번역 실행
            if (finalTranscript) {
                this.translateText(finalTranscript);
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            let errorMsg = '음성 인식 오류가 발생했습니다.';

            switch (event.error) {
                case 'no-speech':
                    errorMsg = '음성이 감지되지 않았습니다. 다시 시도해주세요.';
                    break;
                case 'audio-capture':
                    errorMsg = '마이크를 찾을 수 없습니다. 마이크 권한을 확인해주세요.';
                    break;
                case 'not-allowed':
                    errorMsg = '마이크 사용 권한이 거부되었습니다. 브라우저 설정에서 마이크 권한을 허용해주세요.';
                    break;
            }

            this.showStatus(errorMsg, 'error');
        };
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
        // API 키 로드
        if (this.apiKey) {
            this.apiKeyInput.value = this.apiKey;
        }

        // 언어 설정 로드
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
            this.recognition.stop();
        } else {
            this.updateRecognitionLanguage();
            this.recognition.start();
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
        // 기존 기록과 현재 텍스트 합쳐서 표시
        let html = '';

        // 기존 번역된 문장들
        this.translationHistory.forEach(item => {
            html += `<p class="history-item">${item.source}</p>`;
        });

        // 현재 입력 중인 텍스트
        if (currentText) {
            html += `<p class="${isInterim ? 'interim' : 'current'}">${currentText}</p>`;
        }

        this.sourceText.innerHTML = html || '<p class="placeholder">시작 버튼을 눌러 말하세요...</p>';
    }

    displayTargetText() {
        let html = '';

        this.translationHistory.forEach(item => {
            html += `<p class="history-item">${item.target}</p>`;
        });

        this.targetText.innerHTML = html || '<p class="placeholder">번역 결과가 여기에 표시됩니다...</p>';
    }

    async translateText(text) {
        if (!this.apiKey) {
            this.showStatus('API 키를 입력해주세요. Hugging Face에서 무료로 발급받을 수 있습니다.', 'warning');
            return;
        }

        // 번역 중 표시 추가
        let tempHtml = '';
        this.translationHistory.forEach(item => {
            tempHtml += `<p class="history-item">${item.target}</p>`;
        });
        tempHtml += '<p class="translating">번역 중... <span class="loading"></span></p>';
        this.targetText.innerHTML = tempHtml;

        const langNames = {
            ko: 'Korean', en: 'English', ja: 'Japanese', zh: 'Chinese',
            es: 'Spanish', fr: 'French', de: 'German', pt: 'Portuguese',
            ru: 'Russian', ar: 'Arabic', hi: 'Hindi', vi: 'Vietnamese',
            th: 'Thai', id: 'Indonesian'
        };

        const sourceLangName = langNames[this.sourceLang.value];
        const targetLangName = langNames[this.targetLang.value];

        const prompt = `<start_of_turn>user
Translate the following text from ${sourceLangName} to ${targetLangName}. Only output the translation, nothing else.

${text}<end_of_turn>
<start_of_turn>model
`;

        try {
            const response = await fetch(
                'https://api-inference.huggingface.co/models/google/translategemma-12b-it',
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.apiKey}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        inputs: prompt,
                        parameters: {
                            max_new_tokens: 512,
                            temperature: 0.3,
                            do_sample: true,
                            return_full_text: false
                        }
                    })
                }
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));

                if (response.status === 401) {
                    throw new Error('API 키가 유효하지 않습니다.');
                } else if (response.status === 503) {
                    this.showStatus('모델을 로딩 중입니다. 잠시 후 다시 시도해주세요...', 'warning');
                    return;
                } else {
                    throw new Error(errorData.error || `HTTP ${response.status} 오류`);
                }
            }

            const data = await response.json();
            let translation = '';

            if (Array.isArray(data) && data[0]?.generated_text) {
                translation = data[0].generated_text.trim();
            } else if (data.generated_text) {
                translation = data.generated_text.trim();
            } else {
                throw new Error('예상치 못한 응답 형식입니다.');
            }

            // 불필요한 토큰 제거
            translation = translation
                .replace(/<end_of_turn>/g, '')
                .replace(/<start_of_turn>.*?/g, '')
                .trim();

            // 번역 기록에 추가
            this.translationHistory.push({
                source: text,
                target: translation,
                timestamp: new Date().toISOString()
            });

            // 화면 업데이트
            this.displaySourceText('');
            this.displayTargetText();

            this.showStatus('번역 완료!', 'success');
            setTimeout(() => {
                if (this.isListening) {
                    this.showStatus('음성을 듣고 있습니다... (실시간 번역 중)', 'info');
                } else {
                    this.hideStatus();
                }
            }, 1000);

        } catch (error) {
            console.error('Translation error:', error);
            this.showStatus(`번역 오류: ${error.message}`, 'error');
            this.displayTargetText();
        }
    }

    clearAll() {
        // 모든 기록 초기화
        this.translationHistory = [];
        this.currentSourceText = '';

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

        // 텍스트 파일 내용 생성
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

        // 파일 다운로드
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

        this.showStatus(`${filename} 파일로 저장되었습니다.`, 'success');
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
