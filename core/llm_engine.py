import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv
from core.gemini_oauth import GeminiOAuthManager
from core.compat import get_resource_path

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
당신은 최고의 Adobe Photoshop & Illustrator 전문 아트 디렉터이자 ExtendScript(JSX) 엔지니어입니다.
사용자의 자연어 지시와 현재 열린 문서의 상태(JSON), 이전 대화 내역을 종합적으로 분석하여 다음 중 하나를 결정하세요.

======================================================================
🌟 [핵심 디자인 철학: Human-Designer Aesthetics (Anti-AI Slop Guardrails)]
AI가 만든 것 같은 촌스러운 티(AI Slop)를 철저히 배제하고, 인간 프로 디자이너가 작업한 것 같은 세련된 완성도를 보장하세요:
1. 🚫 촌스러운 사이버틱 보라/형광 청록 네온 그라데이션 남발 절대 금지
2. 🚫 캔버스를 무의미한 장식과 그래픽으로 빽빽하게 채우는 과밀 배치 금지
3. ✅ 의도적인 호흡 여백(White Space): 캔버스 상하좌우 최소 15~20%의 안전 마진을 반드시 확보하세요.
4. ✅ 명확한 3단 폰트 스케일(Visual Hierarchy): 대제목(Hero/H1)은 압도적으로 크고 굵게, 부제목(H2)과 본문(Body)은 정돈된 크기로 시선의 흐름을 만드세요.
5. ✅ 감각적인 톤다운 & 에디토리얼 컬러: 매트한 슬레이트, 웜 뉴트럴, 감성 파스텔, 신뢰감 있는 딥 톤 위주로 사용하세요.
6. ✅ 칼같은 기준선 그리드 정렬: 모든 텍스트와 박스는 좌측 또는 중앙 기준선에 완벽히 정렬하세요.
======================================================================

[판단 기준]
1. action: "execute" (즉시 실행)
   - 사용자의 지시가 구체적이고 명확할 때 (예: "가로 800 세로 600 새 문서 만들어줘", "글자 크기를 30pt로 바꾸고 빨간색으로 변경해줘", "중앙에 파란색 원 하나 그려줘")
   - 사용자가 이전 질문에 대해 답변을 주어 세부 조건이 충족되었을 때
   -> 위 Human-Design 원칙을 준수하여 바로 실행 가능한 최적의 ExtendScript (JSX) 코드를 작성하세요.

2. action: "ask" (역질문 및 옵션 제안)
   - 사용자의 지시가 포괄적이거나, 레이아웃/색상 톤/문구/사이즈 등 핵심 디자인 결정이 누락되어 있을 때 (예: "여름 이벤트 배너 만들어줘", "유튜브 썸네일 디자인해줘", "로고 멋지게 꾸며줘")
   - 사용자에게 명확하고 친절하게 2~3가지 핵심 선택지나 질문을 마크다운 형식으로 제시하세요.

[출력 형식 - 반드시 유효한 JSON 하나만 마크다운 코드블록 안에 출력하세요]
```json
{{
  "action": "execute",
  "code": "/* 순수 ExtendScript(JSX) 코드 */",
  "summary": "작업 내용 요약"
}}
```
또는
```json
{{
  "action": "ask",
  "question": "### 🎨 디자인 작업을 위해 몇 가지를 여쭤볼게요!\\n1. **사이즈**: ...\\n2. **색상 톤**: ...",
  "summary": "추가 정보 확인 필요"
}}
```

[사용 가능한 디자인 스킬 라이브러리 및 헬퍼]
다음 스킬 라이브러리 함수들을 코드 내에 자유롭게 포함하거나 응용하여 프로페셔널한 디자인을 작성하세요:
{load_skills_summary()}

[ExtendScript 작성 시 필수 규칙]
1. Illustrator: app.documents.add(DocumentColorSpace.RGB, w, h), doc.pathItems, doc.textFrames 등 DOM API를 정확하게 준수하세요.
2. 색상 설정: var col = new RGBColor(); col.red = ...; (또는 PaletteSkill.hexToRgb("#RRGGBB") 활용)
3. 코드 마지막에 `return JSON.stringify({{"success": true, "message": "요약"}});` 형식으로 결과를 반환하도록 작성하세요.
"""


class LLMEngine:
    """Natural Language to ExtendScript Generator with Smart Clarification & Self-Healing."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or os.getenv("LLM_PROVIDER", "gemini_oauth")).lower()
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.custom_base_url = os.getenv("CUSTOM_BASE_URL", "http://localhost:11434/v1")
        self.oauth_manager = GeminiOAuthManager()
        self.history: List[Dict[str, str]] = []

    def clear_history(self):
        """Reset conversation context history."""
        self.history = []

    def _call_gemini_oauth(self, messages: List[Dict[str, str]]) -> str:
        """Call Gemini REST API using Google OAuth 2.0 Bearer Access Token."""
        token = self.oauth_manager.get_valid_token()
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
        
        system_instruction = None
        contents = []
        
        for m in messages:
            if m["role"] == "system":
                system_instruction = {"parts": [{"text": m["content"]}]}
            elif m["role"] == "user":
                contents.append({"role": "user", "parts": [{"text": m["content"]}]})
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
                "temperature": 0.3,
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

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call LLM based on configured provider."""
        if self.provider == "gemini_oauth" or self.provider == "gemini":
            return self._call_gemini_oauth(messages)

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
                temperature=0.3
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
                temperature=0.3
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

    def process_prompt(
        self,
        user_prompt: str,
        doc_state: Dict[str, Any],
        bridge: Any,
        target_app: str = "illustrator",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Analyze intent, ask questions if needed, or execute code with self-healing."""
        current_context = f"[현재 {target_app} 문서 상태]\n{json.dumps(doc_state, ensure_ascii=False, indent=2)}\n\n[사용자 지시]\n{user_prompt}"
        
        messages = [{"role": "system", "content": SYSTEM_DECISION_PROMPT}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": current_context})

        raw_response = self._call_llm(messages)
        decision = self.extract_json_or_code(raw_response)

        # 1. If LLM decides to ask clarifying questions
        if decision.get("action") == "ask":
            question_text = decision.get("question", raw_response)
            self.history.append({"role": "user", "content": user_prompt})
            self.history.append({"role": "assistant", "content": question_text})
            return {
                "action": "ask",
                "question": question_text,
                "summary": decision.get("summary", "")
            }

        # 2. If LLM decides to execute code
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
