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
당신은 사용자의 지시, 현재 열린 문서의 텍스트 DOM 상태(JSON), **그리고 실시간 캔버스 캡처 이미지(Vision)**를 모두 보고 판단합니다.

======================================================================
🚨 [판단 및 질문 규칙 (STRICT CO-PILOT POLICY)]

1. 다음의 경우에는 절대로 바로 코드를 실행하지 말고, 반드시 **action: "ask"** 로 질문하세요:
   - 새로운 디자인/배너/포스터/카드 제작 요청 시 (예: "한의원 배너 만들어줘", "새 파일 만들고 홍보물 짜줘")
   - 주관적인 피드백이나 개선 요청 시 (예: "폰트가 구린데", "느낌이 별로야", "색상이 맘에 안 들어", "더 세련되게 바꿔줘")
   - 디자인 선택지가 여러 가지 존재할 때
   -> 2~3가지 명확하고 매력적인 선택지를 번호 매겨 친절하게 제안하세요.

2. 다음의 경우에만 **action: "execute"** (즉시 실행) 하세요:
   - 사용자가 이전 질문에 대해 특정 번호나 선택지를 답변했을 때 (예: "1번 명조체로 해줘", "가로 A4에 세이지 그린 톤으로 가자")
   - 수치나 대상이 명확한 단일 수정 명령일 때 (예: "제목 글자 크기를 50pt로 키워줘", "배경색을 #1D3A2F로 바꿔줘")

======================================================================
🌟 [핵심 디자인 철학: Human-Designer Aesthetics (Anti-AI Slop Guardrails)]
1. 🚫 촌스러운 사이버틱 보라/형광 청록 네온 그라데이션 남발 절대 금지
2. 🚫 캔버스를 무의미한 장식과 그래픽으로 빽빽하게 채우는 과밀 배치 금지
3. ✅ 의도적인 호흡 여백(White Space 20% 이상)과 칼같은 기준선 그리드 정렬
4. ✅ 명확한 3단 폰트 스케일(Hero -> Sub -> Body)과 감각적인 톤다운 에디토리얼 컬러
5. 🖼️ **실제 이미지 배치 (Image Placement)**:
   - 사진이 준비되어 제공된 경우, ImageSkill.placeImage(imagePath, top, left, width, height)를 사용하여 실제 다운로드된 사진 파일을 캔버스에 직접 배치하고, 필요한 경우 ImageSkill.clipWithRoundedRect로 깔끔한 둥근 마스크를 씌우세요.
======================================================================

[출력 형식 - 반드시 유효한 JSON 하나만 마크다운 코드블록 안에 출력하세요]
```json
{{
  "action": "ask",
  "question": "### 🎨 디자인 작업을 위해 몇 가지를 여쭤볼게요!\\n1. **폰트 스타일**: ...\\n2. **레이아웃 구도**: ...",
  "summary": "방향성 선택 질문"
}}
```
또는 (구체적 답변이나 명확한 단일 수정일 때만)
```json
{{
  "action": "execute",
  "code": "/* 순수 ExtendScript(JSX) 코드 */",
  "summary": "작업 내용 요약"
}}
```

[사용 가능한 디자인 스킬 라이브러리 및 헬퍼]
{load_skills_summary()}

[ExtendScript 작성 시 필수 규칙]
1. Illustrator DOM: app.activeDocument, doc.pathItems, doc.textFrames, doc.placedItems 등을 정확하게 사용하세요.
2. 폰트 적용 시: TypographySkill.koreanFonts 매핑 테이블의 검증된 PostScript 이름을 우선 사용하세요.
3. 코드 마지막에 `return JSON.stringify({{"success": true, "message": "요약"}});` 형식으로 결과를 반환하도록 작성하세요.
"""


class LLMEngine:
    """Natural Language to ExtendScript Generator with Multimodal Vision & Smart Clarification."""

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

    def _call_gemini_oauth(self, messages: List[Dict[str, Any]], image_base64: Optional[str] = None) -> str:
        """Call Gemini REST API using Google OAuth 2.0 with optional Vision Multimodal image payload."""
        token = self.oauth_manager.get_valid_token()
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
        
        system_instruction = None
        contents = []
        
        for m in messages:
            if m["role"] == "system":
                system_instruction = {"parts": [{"text": m["content"]}]}
            elif m["role"] == "user":
                parts = []
                if image_base64 and m == messages[-1]:
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_base64
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
                "maxOutputTokens": 4096
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

    def _call_llm(self, messages: List[Dict[str, Any]], image_base64: Optional[str] = None) -> str:
        """Call LLM based on configured provider."""
        if self.provider == "gemini_oauth" or self.provider == "gemini":
            return self._call_gemini_oauth(messages, image_base64)

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
    def extract_json_or_code(raw_text: str) -> Dict[str, Any]:
        """Extract structured JSON decision or fallback to raw code execution."""
        match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", raw_text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        try:
            return json.loads(raw_text.strip())
        except json.JSONDecodeError:
            pass

        code_match = re.search(r"```(?:javascript|jsx|js)?\s*([\s\S]*?)\s*```", raw_text)
        if code_match:
            return {
                "action": "execute",
                "code": code_match.group(1).strip(),
                "summary": "코드 즉시 실행"
            }

        return {
            "action": "ask",
            "question": raw_text.strip(),
            "summary": "안내 메시지"
        }

    def _auto_resolve_images(self, user_prompt: str) -> Dict[str, str]:
        """Check if user prompt needs photos, auto-resolve via Pinterest, Local path, or Stock search."""
        resolved = {}
        
        # Check if user prompt mentions images, photos, pinterest, local paths
        needs_image = any(w in user_prompt for w in ["사진", "이미지", "포토", "photo", "image", "핀터레스트", "pinterest", "http", ":/"])
        if needs_image:
            img_path = StockImageManager.resolve_image(user_prompt)
            if img_path:
                resolved["matched_image"] = img_path

        return resolved

    def process_prompt(
        self,
        user_prompt: str,
        doc_state: Dict[str, Any],
        bridge: Any,
        target_app: str = "illustrator",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Analyze intent with Vision Multimodal, ask questions if needed, or execute code."""
        # 1. Capture real-time canvas visual snapshot for Vision AI
        canvas_b64 = None
        try:
            canvas_b64 = bridge.capture_canvas_snapshot()
        except Exception:
            canvas_b64 = None

        # 2. Check and auto-download stock/pinterest/local photos if needed
        resolved_images = self._auto_resolve_images(user_prompt)
        img_context = ""
        if resolved_images:
            img_context = f"\n\n[준비된 이미지 파일 경로 (ExtendScript에서 ImageSkill.placeImage로 즉시 사용 가능)]:\n"
            for k, p in resolved_images.items():
                img_context += f"- {k}: '{p}'\n"

        current_context = (
            f"[현재 {target_app} 문서 텍스트 DOM 상태]\n"
            f"{json.dumps(doc_state, ensure_ascii=False, indent=2)}"
            f"{img_context}\n\n"
            f"[사용자 지시]\n{user_prompt}"
        )
        
        messages = [{"role": "system", "content": SYSTEM_DECISION_PROMPT}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": current_context})

        raw_response = self._call_llm(messages, image_base64=canvas_b64)
        decision = self.extract_json_or_code(raw_response)

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
                {"role": "user", "content": f"[이전 실행 코드]\n```javascript\n{code}\n```\n\n[오류 발생]\n{last_error}\n\n오류를 해결한 올바른 JSON(action: execute, code: ...) 형식으로 다시 작성하세요."}
            ]
            fix_raw = self._call_llm(fix_messages)
            fix_decision = self.extract_json_or_code(fix_raw)
            code = fix_decision.get("code", "")

        return {
            "action": "execute",
            "success": False,
            "attempts": attempt,
            "error": last_error,
            "last_code": code
        }
