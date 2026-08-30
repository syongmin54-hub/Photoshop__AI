# 🎨 Adobe AI Co-Pilot (Photoshop & Illustrator Automation)

> **자연어로 지시하는 무손실 디자인 자동화 시스템**  
> 생성형 AI의 한계(저화질, 레이어 병합, 부분 수정 불가)를 해결하고, **실제 Adobe Photoshop & Illustrator 엔진을 자연어로 직접 제어**하는 지능형 디자인 어시스턴트입니다.

---

## ✨ 주요 특징 (Key Features)

1. **무손실 원본 보존 (Lossless Vector & Layer Control)**
   - Adobe 공식 COM 및 ExtendScript(JSX) 엔진을 직접 조종하여 텍스트, 벡터 패스, 레이어 스타일, 색상 프로필을 100% 무손실로 작업합니다.
2. **양방향 스마트 질문 & 제안 (Smart Clarification Co-Pilot)**
   - 구체적인 지시는 **즉시 실행**하고, 모호한 지시는 **AI 아트 디렉터가 2~3가지 핵심 옵션(사이즈, 컬러 톤, 문구)을 먼저 질문**하여 완성도를 높입니다.
3. **인간 디자이너 감성 주입 (Human-Designer Aesthetics / Anti-AI Slop)**
   - 촌스러운 사이버틱 네온 그라데이션을 배제하고, **미니멀 에디토리얼 레이아웃, 의도적인 20% 여백, 황금비율 폰트 위계, 칼같은 그리드 정렬**을 보장합니다.
4. **검증된 디자인 스킬 라이브러리 탑재 (`skills/`)**
   - **Auto-Layout**: 텍스트 길이에 맞춰 자동으로 늘어나는 스마트 패딩 배경 박스
   - **Palette Generator**: HEX 색상 변환 및 테마별 감성 컬러 하모니
   - **Typography Stylist**: 3단계 글꼴 계층 및 가독성 최적화
   - **Batch Exporter**: 고해상도 PNG24 / SVG / PDF 무손실 내보내기
5. **Google OAuth 구독/무료 연동 (비용 0원)**
   - 유료 API 키 없이, 본인의 Google 계정 로그인으로 **Gemini 3.7 Flash** 최신 플래그십 모델을 무료로 사용합니다.

---

## 🚀 빠른 시작 (Getting Started)

### 1. 실행 파일(.exe)로 실행 (추천)
- `dist/AdobeAI.exe`를 더블클릭하여 바로 실행합니다. (Python 설치 불필요)

### 2. 소스 코드로 실행
```bash
# 1. 저장소 클론
git clone https://github.com/your-username/Photoshop__AI.git
cd Photoshop__AI

# 2. 의존성 설치
pip install -r requirements.txt

# 3. CLI 실행
python main.py
```

---

## 💡 사용 방법 및 명령어

터미널 CLI에서 자연어로 편하게 작업 지시를 입력하세요:

```text
Illustrator > 가로 1080 세로 1080 새 문서 만들고 다크 테마 배경에 'AURA COFFEE' 신메뉴 포스터 만들어줘
Illustrator > 현재 캔버스에 있는 타이틀 글자 크기를 48pt로 키우고 웜 베이지 컬러로 바꿔줘
Illustrator > /inspect      (현재 캔버스의 레이어/텍스트 실시간 분석)
Illustrator > /target ps    (포토샵으로 작업 대상 전환)
Illustrator > /reset        (대화 맥락 초기화)
```

---

## 🛠️ 기술 스택 (Tech Stack)

- **Language & Framework**: Python 3.10+, PyWin32 (Windows COM Automation)
- **Scripting Engine**: Adobe ExtendScript (ECMAScript 3 / JSX)
- **LLM Engine**: Google Gemini 3.7 Flash via Google OAuth 2.0
- **CLI Interface**: Rich Terminal UI

---

## 📄 라이선스 (License)

MIT License
