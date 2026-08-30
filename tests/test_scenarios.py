import sys
import time
import json
import importlib
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import core.llm_engine
import core.bridge_ai
import core.inspector
importlib.reload(core.llm_engine)
importlib.reload(core.bridge_ai)
importlib.reload(core.inspector)

from core.bridge_ai import IllustratorBridge
from core.inspector import DocumentInspector
from core.llm_engine import LLMEngine


def run_scenario(name: str, prompt: str, follow_up: str = ""):
    print(f"\n========================================================")
    print(f"🎬 [시나리오 실행: {name}]")
    print(f"========================================================")
    
    bridge = IllustratorBridge()
    bridge.connect()
    
    llm = LLMEngine()
    llm.clear_history()
    
    # 1. Inspect initial document state
    doc_state = DocumentInspector.inspect_illustrator(bridge)
    print(f"초기 문서: {doc_state.get('name')} (아트보드: {len(doc_state.get('artboards', []))}개)")
    
    # 2. First Prompt Turn
    t0 = time.time()
    res1 = llm.process_prompt(prompt, doc_state, bridge)
    t1 = time.time() - t0
    
    print(f"[Turn 1] 응답 속도: {t1:.2f}s | Action: {res1.get('action')}")
    if res1.get("action") == "ask":
        print(f"👉 AI 디렉터 역질문:\n{res1.get('question')[:250]}...\n")
        
        # 3. Follow-up Turn
        if follow_up:
            print(f"💬 사용자 답변: '{follow_up}'")
            doc_state = DocumentInspector.inspect_illustrator(bridge)
            t2_0 = time.time()
            res2 = llm.process_prompt(follow_up, doc_state, bridge)
            t2 = time.time() - t2_0
            print(f"[Turn 2] 응답 속도: {t2:.2f}s | Action: {res2.get('action')} | Success: {res2.get('success')}")
            print(f"결과: {res2.get('result')}")
    else:
        print(f"결과: {res1.get('result')}")

    # 4. Decomposed Inspection Verification
    final_state = DocumentInspector.inspect_illustrator(bridge)
    print(f"\n📊 [실시간 분해 요소 검증 결과]")
    print(f"- 아트보드(페이지) 수: {len(final_state.get('artboards', []))}개")
    print(f"- 분해된 텍스트 요소: {len(final_state.get('textElements', []))}개")
    print(f"- 분해된 이미지 요소: {len(final_state.get('imageElements', []))}개")
    print(f"- 분해된 도형/카드: {len(final_state.get('shapeElements', []))}개")
    
    for tf in final_state.get('textElements', [])[:4]:
        print(f"  • 텍스트: '{tf.get('content')}' | 폰트: {tf.get('fontPostScript')} | 색상: {tf.get('color')} | Y: {tf.get('top')}")


if __name__ == "__main__":
    # Test 1: Single Promotional Banner
    run_scenario(
        "1. 단일 A4 홍보 배너",
        "A4 가로 크기로 신뢰감 있는 한의원 홍보 배너 제작해줘",
        "1번 헤리티지 프리미엄 스타일로 완성해줘"
    )

    # Test 2: Multi-page Card News (4 Slides)
    run_scenario(
        "2. 4장 다중 카드뉴스",
        "1080x1080 크기 4장짜리 인스타그램 카드뉴스로 '환절기 면역력 한방 건강 상식' 제작해줘",
        ""
    )

    # Test 3: Large X-Banner
    run_scenario(
        "3. 대형 세로 X-배너 (600x1800mm)",
        "신규 오픈 기념 600x1800mm 세로 X-배너 디자인해줘",
        "1번 다크 네이비 럭셔리 골드 포인트 스타일로 배치해줘"
    )
