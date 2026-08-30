<div align="center">

# 🎨 Adobe AI Co-Pilot
### 자연어로 지시하는 무손실 디자인 자동화 & 멀티모달 비전 어시스턴트

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Gemini 3.7 Flash](https://img.shields.io/badge/AI%20Engine-Gemini%203.7%20Flash%20Vision-orange.svg)](https://deepmind.google/technologies/gemini/)
[![Adobe Compatible](https://img.shields.io/badge/Adobe-Photoshop%20%26%20Illustrator-ff1493.svg)](https://www.adobe.com/)
[![Zero Cost](https://img.shields.io/badge/Cost-100%25%20Free%20(Google%20OAuth)-success.svg)](https://github.com/syongmin54-hub/Photoshop__AI)

<br/>

**생성형 AI의 한계(저화질, 레이어 병합, 특정 부분 수정 불가)를 완벽히 해결합니다.**  
실제 **Adobe Photoshop & Illustrator의 텍스트, 벡터 패스, 레이어 엔진을 자연어로 직접 제어**하는 차세대 디자인 Co-Pilot입니다.

</div>

---

## 🌟 6대 핵심 차별화 기능 (Key Highlights)

```mermaid
graph TD
    User[사용자 자연어 지시] --> CoPilot[Gemini 3.7 AI Co-Pilot]
    
    subgraph Input Intelligence
        Vision[1. 실시간 캔버스 비전 스냅샷] --> CoPilot
        Photo[2. 핀터레스트 / 스톡 / 로컬 사진 자동 검색] --> CoPilot
        Font[3. 실제 설치된 164종 한글 PostScript 폰트 자동 매핑] --> CoPilot
    end

    subgraph Design Execution
        CoPilot -->|모호한 지시| QnA[4. 3가지 컨셉 스마트 질문 & 제안]
        CoPilot -->|구체적 지시| Engine[5. Anti-AI Slop 인간 디자이너 가드레일]
        Engine --> Skills[6. 전문 스킬 라이브러리 (Auto-Layout, Palette, Masking)]
    end

    Skills --> Canvas[Adobe Illustrator & Photoshop 무손실 적용]
```

### 1. 👁️ 실시간 멀티모달 캔버스 비전 (Vision AI)
- 작업할 때마다 **현재 캔버스를 0.1초 만에 캡처하여 Gemini 3.7 Flash Vision API로 전달**합니다.
- 사진 속 피사체의 위치, 시선 방향, 색감, 여백을 눈으로 직접 보면서 최적의 공간 구도를 잡습니다.

### 2. 📸 멀티 소스 이미지 검색 & 자동 배치 (Multi-Source Photos)
- **핀터레스트 검색**: `"핀터레스트에서 감성 카페 인테리어 사진 검색해서 넣어줘"`
- **핀터레스트 링크 직접 삽입**: `"https://kr.pinterest.com/pin/... 이 사진으로 포스터 만들어줘"`
- **100% 상업용 무료 스톡**: 위키미디어 / 언스플래시 고화질 실사 사진 자동 다운로드 & 라운드 클리핑 마스크 적용
- **내 PC 로컬 사진**: `"D:\사진\원장님.jpg 사진 넣고 배너 꾸며줘"`

### 3. 🎯 스마트 Co-Pilot 양방향 질문 & 옵션 제안
- 신규 제작 요청이나 *"폰트가 구린데"*, *"더 세련되게 바꿔줘"* 같은 주관적 피드백 시, 독단적으로 실행하지 않고 **3가지 디자인 무드/서체/배열 선택지를 먼저 친절하게 질문**합니다.

### 4. 🌿 인간 프로 디자이너 감성 가드레일 (Anti-AI Slop)
- 촌스러운 사이버틱 네온 그라데이션과 과밀 배치를 철저히 배제합니다.
- **20% 의도적 호흡 여백, 3단 폰트 스케일(Hero/Sub/Body), 톤다운 에디토리얼 컬러, 칼같은 기준선 정렬**을 보장합니다.

### 5. 🔤 시스템 한글 폰트 100% 실명 매핑 (Exact Font Resolver)
- 사용자 PC에 설치된 폰트를 실시간 스캔하여, 일러스트레이터가 실제 인식하는 **진짜 PostScript 이름(`KoPubBatangBold`, `NanumSquareNeoTTF-cBd` 등)**으로 정확하게 적용합니다. (폰트 깨짐/기본 폰트 폴백 원천 차단)

### 6. 🚀 완전 무설치 단일 실행 파일 배포 (`AdobeAI.exe`)
- Python, 가상환경, 라이브러리 설치가 전혀 필요 없습니다. **`AdobeAI.exe` 파일 하나만 더블클릭**하면 바로 실행됩니다.

---

## 🚀 빠른 시작 (Quick Start)

### 1. 실행 파일(.exe)로 실행 (비개발자 추천 ⭐)
- `dist/AdobeAI.exe`를 더블클릭하여 실행합니다.
- 최초 1회 **`/login`** 입력 ➔ 본인 Google 계정(무료/구독)으로 1초 로그인하면 끝!

### 2. 소스 코드로 실행
```bash
# 1. 저장소 클론
git clone https://github.com/syongmin54-hub/Photoshop__AI.git
cd Photoshop__AI

# 2. 의존성 설치
pip install -r requirements.txt

# 3. CLI 실행
python main.py
```

---

## 💬 실전 자연어 프롬프트 예시

| 작업 목적 | 추천 프롬프트 예시 |
| :--- | :--- |
| **홍보 배너 제작** | `적절한 한약/침 사진 찾아서 넣고 A4 가로 한의원 홍보 배너 제작해줘` |
| **핀터레스트 활용** | `핀터레스트에서 모던 건축 인테리어 사진 검색해서 우측에 둥근 마스크로 넣어줘` |
| **핀 링크 직접 삽입** | `https://kr.pinterest.com/pin/12345/ 이 사진 넣고 감성 카페 메뉴판 만들어줘` |
| **디자인 피드백/수정** | `폰트가 너무 구린데` *(AI가 3가지 타이포 스타일을 제안함)* |
| **로컬 사진 활용** | `D:\Photos\product.png 사진 중앙에 배치하고 네온 뱃지 달아줘` |
| **실시간 캔버스 인스펙션**| `/inspect` *(현재 열린 캔버스의 레이어/텍스트 실시간 분석)* |

---

## ⌨️ CLI 내장 명령어

| 명령어 | 설명 |
| :--- | :--- |
| `/login` | Google 계정 OAuth 로그인 (토큰 자동 발급/영구 갱신) |
| `/inspect` | 현재 캔버스의 레이어, 텍스트, 바운딩 박스 상세 구조 JSON 확인 |
| `/status`, `/info` | 현재 연결된 Adobe 프로그램(AI / PS) 및 열린 문서 상태 확인 |
| `/new` | 새 캔버스/아트보드 문서 생성 |
| `/target [ai\|ps]` | 작업 대상 프로그램 전환 (Illustrator ↔ Photoshop) |
| `/reset`, `/clear` | 이전 대화 맥락 및 디자인 히스토리 초기화 |
| `/help` | 도움말 표시 |
| `/exit`, `/quit` | 프로그램 종료 |

---

## 📁 프로젝트 구조

```text
Photoshop__AI/
├── core/
│   ├── bridge_ai.py       # Illustrator COM & 고속 비전 스냅샷 캡처
│   ├── bridge_ps.py       # Photoshop COM & 트랜잭션 브릿지
│   ├── compat.py          # Windows COM / 리소스 경로 리졸버
│   ├── gemini_oauth.py    # Google OAuth 2.0 매니저 (비용 0원 연동)
│   ├── image_search.py    # 핀터레스트 / 스톡 / 로컬 멀티 소스 이미지 리졸버
│   ├── inspector.py       # 실시간 레이어 & 텍스트 DOM 인스펙터
│   ├── json_polyfill.py   # ExtendScript $.global.JSON 폴리필
│   └── llm_engine.py      # Multimodal Vision & Smart Co-Pilot 엔진
├── skills/
│   ├── auto_layout.jsx         # 스마트 패딩 박스 및 요소 균등 분배
│   ├── batch_exporter.jsx      # 고해상도 PNG24 / SVG / PDF 내보내기
│   ├── human_design_rules.jsx  # Anti-AI Slop 인간 디자이너 가드레일
│   ├── image_manager.jsx       # 실사 이미지 캔버스 삽입 & 둥근 클리핑 마스크
│   ├── palette_generator.jsx   # HEX 색상 변환 및 트렌디 컬러 팔레트
│   └── typography_stylist.jsx  # 실제 설치 폰트 매핑 & 황금비율 타이포
├── dist/
│   └── AdobeAI.exe             # 🚀 배포용 단일 실행 파일 (25.8 MB)
├── .env.example                # 설정 샘플 템플릿
├── .gitignore                  # Git 보안 제외 목록 (토큰/키 유출 방지)
└── README.md                   # 프로젝트 공식 문서
```

---

## 📄 라이선스 (License)

MIT License - 자유롭게 수정 및 상업적 배포가 가능합니다.
