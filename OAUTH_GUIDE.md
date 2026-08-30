# Google OAuth 2.0 연동 가이드

API 키 없이 본인의 **Google 계정(Gemini 구독/무료 포함)**으로 프로그램을 사용하려면 최초 1회 Google OAuth 클라이언트 등록이 필요합니다.

---

### 1단계: Google Cloud Console에서 OAuth 클라이언트 생성 (무료, 1분 소요)

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속합니다.
2. 상단 프로젝트 선택에서 새 프로젝트를 생성합니다. (예: `Adobe-AI-Automation`)
3. 좌측 메뉴 **[API 및 서비스] → [OAuth 동의 화면]**:
   - 사용자 유형: **외부(External)** 선택 후 만들기.
   - 앱 이름: `Adobe Controller` 입력 후 저장.
4. 좌측 메뉴 **[API 및 서비스] → [사용자 인증 정보]**:
   - 상단 **[+ 사용자 인증 정보 만들기] → [OAuth 클라이언트 ID]** 클릭.
   - 애플리케이션 유형: **데스크톱 앱(Desktop App)** 선택.
   - 이름: `Adobe-CLI` 입력 후 만들기.
5. 생성된 OAuth 클라이언트에서 **[JSON 다운로드]**를 클릭합니다.
6. 다운로드한 파일의 이름을 **`client_secret.json`**으로 변경하여 이 프로젝트 폴더(`D:\04 coding\Photoshop__AI\`)에 넣습니다.

---

### 2단계: 로그인 및 사용

터미널에서 프로그램을 실행한 뒤:
```bash
python main.py
```
1. CLI에서 `/login`을 입력하면 브라우저가 열리며 Google 로그인 창이 뜹니다.
2. Gemini 구독 계정으로 로그인 및 권한 승인 완료.
3. 이후에는 `gemini_token.json`에 토큰이 자동 저장 및 자동 갱신되어 영구적으로 로그인 없이 바로 자연어 명령을 사용할 수 있습니다.
