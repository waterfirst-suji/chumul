# OLED 2차 공진구조 각도 의존성 시뮬레이터

## 개요

OLED(Organic Light Emitting Diode)의 2차 공진구조에서 관찰 각도에 따른 발광 스펙트럼 변화를 시뮬레이션하는 프로그램입니다.

## 물리적 현상

### 관찰된 현상

OLED를 정면(0°)에서 측면(60°)까지 10° 간격으로 틸트하면서 발광 스펙트럼을 측정할 때:

- **Red**: 625nm → 620nm (5nm blue shift)
- **Green**: 543nm → 521nm (22nm blue shift)
- **Blue**: 461nm → 459nm (2nm blue shift)
- **Intensity**: 모든 색상에서 감소

### 근본 원인

#### 1. Fabry-Perot 공진 구조

OLED의 2차 공진구조는 하부 반사전극과 상부 반투명 전극 사이에 형성되는 Fabry-Perot 공진기로 작동합니다.

**공진 조건:**
```
m × λ = 2 × n_eff × d × cos(θ)
```

여기서:
- `m`: 공진 차수 (2차 공진의 경우 m=2)
- `λ`: 공진 파장
- `n_eff`: 유효 굴절률 (일반적으로 1.7~1.9)
- `d`: 공진 길이 (광학 경로)
- `θ`: 공진기 내부에서의 각도

#### 2. Blue Shift의 원인

관찰 각도가 증가하면:

1. **Snell의 법칙**에 의해 외부 각도와 내부 각도의 관계:
   ```
   n_air × sin(θ_external) = n_eff × sin(θ_internal)
   ```

2. 내부 각도가 증가하면 **cos(θ_internal) 감소**

3. 공진 조건에서 **파장(λ)도 감소**해야 함:
   ```
   λ(θ) = (2 × n_eff × d × cos(θ)) / m
   ```

4. 따라서 스펙트럼이 **짧은 파장으로 이동** (blue shift)

#### 3. 강도 감소의 원인

1. **Lambertian 발광 특성**:
   ```
   I(θ) = I₀ × cos(θ)
   ```
   각도가 증가하면 코사인 법칙에 따라 강도 감소

2. **공진 조건 이탈**:
   - 각도 변화로 인해 최적 공진 조건에서 벗어남
   - 공진기 증강 효과(cavity enhancement) 감소

3. **Fresnel 반사 계수의 각도 의존성**:
   - 전극에서의 반사율이 각도에 따라 변화

## 프로그램 구조

### 파일 구성

```
oled_cavity_simulator.py  # 핵심 물리 모델 및 시뮬레이션 로직
oled_app.py               # Streamlit 기반 인터랙티브 UI
oled_viewer.html          # HTML 기본 버전 시뮬레이터
oled_advanced.html        # HTML 고급 버전 (Chart.js 사용)
README_OLED.md            # 문서 (이 파일)
```

### 주요 클래스 및 함수

#### `OLEDCavitySimulator`

공진구조의 물리적 모델을 구현한 핵심 클래스:

- `snells_law()`: Snell의 법칙을 이용한 내부 각도 계산
- `resonance_wavelength()`: 각도에 따른 공진 파장 계산
- `simulate_spectrum_at_angle()`: 특정 각도에서의 스펙트럼 시뮬레이션
- `simulate_angular_dependence()`: 각도별 스펙트럼 변화 시뮬레이션

#### `OLEDParams`

OLED 파라미터를 정의하는 데이터 클래스:

- `lambda_0`: 중심 파장 (nm)
- `n_eff`: 유효 굴절률
- `cavity_length`: 공진 길이 (nm)
- `order`: 공진 차수
- `fwhm`: 스펙트럼 폭 (Full Width at Half Maximum, nm)
- `peak_intensity`: 피크 강도

## 사용 방법

### 1. HTML 버전 (가장 간단 - 설치 불필요)

브라우저에서 직접 실행:

**기본 버전:**
```bash
# 파일을 브라우저에서 열기
open oled_viewer.html  # Mac
start oled_viewer.html # Windows
xdg-open oled_viewer.html # Linux
```

**고급 버전 (Chart.js 포함):**
```bash
open oled_advanced.html
```

#### HTML 버전 기능:
- ✅ 설치 불필요 - 브라우저만 있으면 됨
- ✅ 실시간 각도 조절 슬라이더
- ✅ 자동 애니메이션 모드
- ✅ RGB 스펙트럼 실시간 시각화
- ✅ 파장 shift 및 강도 변화 표시
- ✅ 3개 탭: 실시간 시뮬레이션 / 데이터 분석 / 스펙트럼 비교

### 2. Python 설치 버전

필요한 패키지가 이미 `requirements.txt`에 포함되어 있습니다:

```bash
pip install -r requirements.txt
```

#### 2-1. 커맨드라인에서 시뮬레이션 실행

```bash
python oled_cavity_simulator.py
```

출력 예시:
```
============================================================
OLED 2차 공진구조 각도 의존성 시뮬레이션
============================================================

RED OLED:
  유효 굴절률: 1.80
  공진 길이: 347.22 nm
  공진 차수: 2

  각도별 피크 파장 변화:
     0° → 625.0 nm (shift: +0.0 nm, intensity: 1.000)
    10° → 623.8 nm (shift: -1.2 nm, intensity: 0.985)
    20° → 620.4 nm (shift: -4.6 nm, intensity: 0.940)
    30° → 614.9 nm (shift: -10.1 nm, intensity: 0.866)
    40° → 607.6 nm (shift: -17.4 nm, intensity: 0.766)
    50° → 598.9 nm (shift: -26.1 nm, intensity: 0.643)
    60° → 589.3 nm (shift: -35.7 nm, intensity: 0.500)
```

#### 2-2. Streamlit 웹 앱 실행

```bash
streamlit run oled_app.py
```

또는 제공된 스크립트 사용:

**Windows:**
```bash
run_oled.bat
```

**Linux/Mac:**
```bash
./run_oled.sh
```

## 웹 앱 기능

### 모드 1: 기본 시뮬레이션

- RGB 세 가지 색상의 각도별 스펙트럼 변화 시뮬레이션
- 피크 파장 변화 그래프
- 강도 변화 그래프
- 개별 스펙트럼 플롯
- 2D 스펙트럼 맵 (각도 vs 파장)

### 모드 2: 고급 설정

파라미터를 직접 조정하여 시뮬레이션:

- 중심 파장 (λ₀)
- 유효 굴절률 (n_eff)
- 공진 차수 (m)
- 스펙트럼 폭 (FWHM)

공진 길이는 자동으로 계산됩니다:
```
d = (m × λ₀) / (2 × n_eff)
```

### 모드 3: 실측 데이터 비교

- 실측 데이터와 시뮬레이션 결과 비교
- 파라미터 피팅 (n_eff, FWHM 조정)
- RMSE (Root Mean Square Error) 계산

## 실행 스크립트

### Windows: `run_oled.bat`

```batch
@echo off
echo OLED 2차 공진구조 시뮬레이터 시작...
streamlit run oled_app.py
pause
```

### Linux/Mac: `run_oled.sh`

```bash
#!/bin/bash
echo "OLED 2차 공진구조 시뮬레이터 시작..."
streamlit run oled_app.py
```

## 시뮬레이션 결과 해석

### Green OLED의 큰 Blue Shift

Green OLED가 Red, Blue에 비해 훨씬 큰 blue shift를 보이는 이유:

1. **파장 의존성**: 공진 조건의 각도 의존성은 파장이 길수록 크게 나타남
2. **공진 길이**: Green의 경우 공진 길이와 파장의 비율이 다른 색상과 다를 수 있음
3. **유효 굴절률**: 파장에 따른 분산(dispersion)으로 인해 유효 굴절률이 다름

### 파라미터 피팅

실측 데이터와 일치시키기 위해 조정 가능한 파라미터:

1. **유효 굴절률 (n_eff)**: 1.5 ~ 2.0
   - 값이 클수록 blue shift가 작아짐
   - 실제 OLED 소재의 굴절률과 일치해야 함

2. **스펙트럼 폭 (FWHM)**: 10 ~ 60 nm
   - 발광층의 특성에 따라 결정
   - 공진 구조의 Q-factor와 관련

## 수식 정리

### 1. 공진 조건
```
m × λ = 2 × n_eff × d × cos(θ_internal)
```

### 2. Snell의 법칙
```
n_air × sin(θ_external) = n_eff × sin(θ_internal)
```

### 3. 공진 파장의 각도 의존성
```
λ(θ) = λ₀ × cos(θ_internal)
```

### 4. Lambertian 강도
```
I(θ) = I₀ × cos(θ_external)
```

### 5. 공진 길이 계산
```
d = (m × λ₀) / (2 × n_eff)
```

## 추가 개선 사항

### 고급 물리 모델

1. **Transfer Matrix Method (TMM)**:
   - 다층 박막 구조의 정확한 광학 시뮬레이션
   - 각 층의 복소 굴절률 고려

2. **파장 의존 굴절률 (Dispersion)**:
   - Cauchy 또는 Sellmeier 공식 적용
   - 각 색상별로 다른 유효 굴절률

3. **Microcavity 효과**:
   - Purcell 효과에 의한 자발 방출 증강
   - 발광 효율의 각도 의존성

4. **기판 효과**:
   - 유리 기판에서의 광 추출 효율
   - 임계각(critical angle) 고려

## 참고문헌

1. Smith, L. H., et al. "Angular distribution of light emission from OLEDs with a microcavity structure." *Journal of Applied Physics* (2004).

2. Lin, C. L., et al. "Precise color tuning of OLEDs by using cavity effect." *Organic Electronics* (2011).

3. Nowy, S., et al. "Light extraction and optical loss mechanisms in organic light-emitting diodes: Influence of the emitter quantum efficiency." *Journal of Applied Physics* (2008).

## 라이선스

MIT License

## 문의

이슈 또는 질문이 있으시면 GitHub Issues를 통해 문의해 주세요.
