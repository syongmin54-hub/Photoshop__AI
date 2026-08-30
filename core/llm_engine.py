import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv
from core.gemini_oauth import GeminiOAuthManager
from core.compat import get_resource_path
from core.image_search import StockImageManager

load_dotenv()

def load_skills_summary() -> str:
    """Load core skill helpers to inject into LLM system prompt."""
    skills_dir = get_resource_path("skills")
    skills_text = []
    if skills_dir.exists():
        for f in skills_dir.glob("*.jsx"):
            try:
                content = f.read_text(encoding="utf-8")
                skills_text.append(f"// --- Skill Module: {f.name} ---\n{content}")
            except Exception:
                pass
    return "\n\n".join(skills_text)

SYSTEM_DECISION_PROMPT = f"""
당신은 최고의 Adobe Photoshop & Illustrator 전문 멀티모달 AI 아트 디렉터이자 ExtendScript(JSX) 엔지니어입니다.
당신은 사용자의 지시, **각각 분해된 텍스트/이미지/아트보드 요소 구조(Decomposed DOM)**, 그리고 **페이지별 실시간 비전 스냅샷(Multi-page Vision)**을 모두 면밀히 뜯어보고 분석하여 디자인합니다.

======================================================================
🚨 [최우선 의도 판단 & 실행 분기 규칙 (ACTION DECISION RULES)]

1. ✅ **ACTION: execute (즉시 코드 생성 및 실행 - 최우선 처리)**:
   - 사용자가 특정 크기, 장수, 규격, 텍스트 내용을 주며 제작을 요구할 때 (예: "1080x1080 4장 카드뉴스 만들어줘", "A4 배너 만들어줘", "X-배너 제작해줘")
   - 사용자가 이전 질문에 대해 답변하거나 번호를 선택했을 때 (예: "1번으로 해줘", "2번으로 가자", "명조 스타일로 완성해줘")
   - 수정/정리/조회 명령일 때 (예: "글자 크기 키워줘", "배경색 바꿔줘", "레이아웃 정리해줘")
   -> **즉시 최고의 ExtendScript(JSX) 코드를 작성하여 실행**하세요!

2. ❓ **ACTION: ask (질문 및 옵션 제안)**:
   - 사용자가 아무런 규격/내용/주제 없이 오직 "배너 만들어봐", "디자인 시작해줘" 같은 모호한 단 한마디만 했을 때만 사용하세요.

======================================================================
[출력 형식 - 반드시 아래 포맷을 엄격히 준수하세요]

만약 즉시 실행(execute)하는 경우:
ACTION: execute
SUMMARY: 작업 내용 요약

```javascript
/* 순수 ExtendScript(JSX) 코드 */
```

만약 추가 질문(ask)이 필요한 경우:
ACTION: ask
QUESTION:
### 🎨 디자인 작업을 위해 몇 가지를 여쭤볼게요!
1. **스타일**: ...
2. **레이아웃**: ...

======================================================================
🌟 [핵심 기능 및 지원 영역]
- **단일 페이지/홍보배너/현수막**: A4, X-배너(600x1800mm), 가로형 대형 현수막, 유튜브 썸네일, 웹 배너
- **다중 페이지(카드뉴스 / 슬라이드)**: MultiPageSkill.createMultiPages(4, 1080, 1080) 등을 활용하여 4~10장 카드뉴스 일괄 생성
- **다중 사진 포트폴리오/룩북**: PortfolioSkill.createPhotoGrid(...)를 활용한 복합 갤러리 그리드 레이아웃

======================================================================
🚨 [최우선 필수 규칙: 좌표계 & 가독성 가드레일 (ABSOLUTE RULES)]

1. 📐 **Illustrator 좌표계 절대 준수 (음수 Y좌표 절대 금지!)**:
   - 일러스트레이터의 Y=0은 바닥(Bottom)이고, Y=doc.height가 상단(Top)입니다.
   - 상단에서 100pt 아래에 배치하려면 **반드시 `top = doc.height - 100` (양수)** 공식을 사용하세요!
   - LayoutSystem.setTextPos(tf, left, offsetFromTop) 또는 LayoutSystem.addRect(...) 헬퍼를 적극 활용하세요.

2. 👁️ **배경-텍스트 고대비 가독성 (High Contrast)**:
   - 다크/딥 배경(#122019, 딥그린, 네이비, 블랙 등)에는 **무조건 선명한 화이트(#FFFFFF)나 골드(#D4AF37), 밝은 세이지(#C5E0D0)** 폰트 색상을 적용하세요.
   - 라이트 배경에는 다크 차콜(#18181B) 텍스트를 적용하세요.

3. 🧹 **중복 오브젝트 겹침 방지 (Clean Canvas)**:
   - 전체 재배치나 새 디자인 작업 시, 기존 더러워진 박스/도형들이 겹치지 않도록 `LayoutSystem.clearCanvas()`를 호출하거나 기존 요소를 정리한 후 새로 그리세요.

======================================================================
🌟 [핵심 디자인 철학: Human-Designer Aesthetics (Anti-AI Slop Guardrails)]
1. 🚫 촌스러운 사이버틱 보라/형광 청록 네온 그라데이션 남발 절대 금지
2. 🚫 캔버스를 무의미한 장식과 그래픽으로 빽빽하게 채우는 과밀 배치 금지
3. ✅ 의도적인 호흡 여백(White Space 20% 이상)과 칼같은 기준선 그리드 정렬
4. ✅ 명확한 3단 폰트 스케일(Hero -> Sub -> Body)과 감각적인 톤다운 에디토리얼 컬러

[사용 가능한 디자인 스킬 라이브러리 및 헬퍼]
{load_skills_summary()}

[ExtendScript 작성 시 필수 규칙]
1. Illustrator DOM: app.activeDocument, doc.pathItems, doc.textFrames, doc.placedItems, doc.artboards 등을 정확하게 사용하세요.
2. 폰트 적용 시: TypographySkill.koreanFonts 매핑 테이블의 검증된 PostScript 이름을 우선 사용하세요.
3. 코드 마지막에 `return JSON.stringify({{"success": true, "message": "요약"}});` 형식으로 결과를 반환하도록 작성하세요.
"""


class LLMEngine:
    """Ultra-Fast Decomposed Multimodal Vision & Smart Co-Pilot Engine."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini_oauth")).lower()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.custom_base_url = os.getenv("CUSTOM_BASE_URL", "http://localhost:11434/v1")
        self.oauth_manager = GeminiOAuthManager()
        self.history: List[Dict[str, Any]] = []

    def clear_history(self):
        """Reset conversation context history."""
        self.history = []

    def _call_gemini_oauth(self, messages: List[Dict[str, Any]], image_payloads: Optional[List[Dict[str, str]]] = None) -> str:
        """Call Gemini REST API using Google OAuth 2.0 with multi-page / decomposed image payloads."""
        token = self.oauth_manager.get_valid_token()
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
        
        system_instruction = None
        contents = []
        
        for m in messages:
            if m["role"] == "system":
                system_instruction = {"parts": [{"text": m["content"]}]}
            elif m["role"] == "user":
                parts = []
                if image_payloads and m == messages[-1]:
                    for img in image_payloads:
                        parts.append({
                            "inlineData": {
                                "mimeType": "image/png",
                                "data": img["base64"]
                            }
                        })
                parts.append({"text": m["content"]})
                contents.append({"role": "user", "parts": parts})
            elif m["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": m["content"]}]})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API 오류 ({resp.status_code}): {resp.text}")

        res_data = resp.json()
        try:
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError(f"Gemini 응답 파싱 실패: {res_data}")

    def _call_llm(self, messages: List[Dict[str, Any]], image_payloads: Optional[List[Dict[str, str]]] = None) -> str:
        """Call LLM based on configured provider."""
        if self.provider == "gemini_oauth" or self.provider == "gemini":
            return self._call_gemini_oauth(messages, image_payloads)

        elif self.provider == "openai" or self.provider == "custom":
            import openai
            client = openai.OpenAI(
                api_key=self.openai_key if self.provider == "openai" else "ollama",
                base_url=None if self.provider == "openai" else self.custom_base_url
            )
            model = os.getenv("OPENAI_MODEL", "gpt-4o") if self.provider == "openai" else os.getenv("CUSTOM_MODEL", "llama3")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2
            )
            return response.choices[0].message.content or ""

        elif self.provider == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            system_text = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
            user_messages = [m for m in messages if m["role"] != "system"]
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_text,
                messages=user_messages,
                temperature=0.2
            )
            return response.content[0].text

        else:
            raise ValueError(f"지원하지 않는 LLM 프로바이더입니다: {self.provider}")

    @staticmethod
    def extract_decision(raw_text: str) -> Dict[str, Any]:
        """Extract structured ACTION, SUMMARY, CODE or QUESTION robustly with unclosed block recovery."""
        raw = raw_text.strip()

        # 1. Check for Javascript code block (closed or unclosed)
        code = None
        closed_match = re.search(r"```(?:javascript|jsx|js)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
        if closed_match:
            code = closed_match.group(1).strip()
        else:
            # Check for unclosed code block (e.g. ```javascript at start)
            unclosed_match = re.search(r"```(?:javascript|jsx|js)?\s*([\s\S]+)$", raw, re.IGNORECASE)
            if unclosed_match and ("app." in unclosed_match.group(1) or "function" in unclosed_match.group(1)):
                code = unclosed_match.group(1).strip()

        # Check explicit action and summary headers
        summary_match = re.search(r"^SUMMARY:\s*(.+)$", raw, re.IGNORECASE | re.MULTILINE)
        summary = summary_match.group(1).strip() if summary_match else "디자인 생성 및 실행"

        if code:
            return {
                "action": "execute",
                "code": code,
                "summary": summary
            }

        # 2. JSON Fallback
        first_brace = raw.find('{')
        last_brace = raw.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                parsed = json.loads(raw[first_brace:last_brace+1])
                if isinstance(parsed, dict) and "code" in parsed:
                    return {
                        "action": "execute",
                        "code": parsed.get("code", ""),
                        "summary": parsed.get("summary", "디자인 적용")
                    }
            except Exception:
                pass

        # 3. Question (Ask) Fallback
        q_text = raw
        if "QUESTION:" in raw:
            q_text = raw.split("QUESTION:", 1)[1].strip()

        return {
            "action": "ask",
            "question": q_text,
            "summary": summary
        }

    def process_prompt(
        self,
        user_prompt: str,
        doc_state: Dict[str, Any],
        bridge: Any,
        target_app: str = "illustrator",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Analyze intent with Decomposed Vision Multimodal, ask questions if needed, or execute code."""
        # 1. Capture multi-page decomposed snapshots for Vision AI
        image_payloads = []
        try:
            if hasattr(bridge, "capture_all_artboards_snapshots"):
                pages = bridge.capture_all_artboards_snapshots(scale_percent=15.0)
                for p in pages:
                    image_payloads.append({"name": f"Page_{p['index']}", "base64": p["base64"]})
            elif hasattr(bridge, "capture_canvas_snapshot"):
                b64 = bridge.capture_canvas_snapshot()
                if b64:
                    image_payloads.append({"name": "Canvas", "base64": b64})
        except Exception:
            pass

        # 2. Fast local image check
        local_img = StockImageManager.resolve_image(user_prompt)
        img_context = f"\n\n[사용 가능한 로컬/임시 이미지 파일]: '{local_img}'" if local_img else ""

        current_context = (
            f"[현재 {target_app} 정밀 분해 요소 구조 (Decomposed DOM)]\n"
            f"{json.dumps(doc_state, ensure_ascii=False, indent=2)}"
            f"{img_context}\n\n"
            f"[사용자 지시]\n{user_prompt}"
        )
        
        messages = [{"role": "system", "content": SYSTEM_DECISION_PROMPT}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": current_context})

        raw_response = self._call_llm(messages, image_payloads=image_payloads)
        decision = self.extract_decision(raw_response)

        # A. If LLM decides to ask clarifying questions
        if decision.get("action") == "ask":
            question_text = decision.get("question", raw_response)
            self.history.append({"role": "user", "content": user_prompt})
            self.history.append({"role": "assistant", "content": question_text})
            return {
                "action": "ask",
                "question": question_text,
                "summary": decision.get("summary", "")
            }

        # B. If LLM decides to execute code
        code = decision.get("code", "")
        summary = decision.get("summary", "")

        attempt = 0
        last_error = None

        while attempt < max_retries:
            attempt += 1
            result = bridge.execute_jsx(code)
            
            if result.get("success"):
                self.history.append({"role": "user", "content": user_prompt})
                self.history.append({"role": "assistant", "content": f"작업 완료: {summary}"})
                return {
                    "action": "execute",
                    "success": True,
                    "attempts": attempt,
                    "code": code,
                    "result": result.get("result") or summary
                }

            # Self-healing loop
            last_error = result.get("error", "알 수 없는 오류")
            fix_messages = [
                {"role": "system", "content": SYSTEM_DECISION_PROMPT},
                {"role": "user", "content": f"[이전 실행 코드]\n```javascript\n{code}\n```\n\n[오류 발생]\n{last_error}\n\n오류를 해결한 올바른 ExtendScript 코드를 마크다운 코드블록(```javascript ... ```) 안에 다시 작성하세요."}
            ]
            fix_raw = self._call_llm(fix_messages)
            fix_decision = self.extract_decision(fix_raw)
            code = fix_decision.get("code", "")

        return {
            "action": "execute",
            "success": False,
            "attempts": attempt,
            "error": last_error,
            "last_code": code
        }
