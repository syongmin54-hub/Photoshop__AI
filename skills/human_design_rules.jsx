/**
 * Skill: Human-Designer Aesthetics (Anti-AI Slop Guardrails)
 * AI 특유의 부자연스럽고 촌스러운 디자인 패턴을 배제하고,
 * 실제 프로 그래픽 디자이너가 작업한 것 같은 세련된 레이아웃을 생성하기 위한 핵심 원칙입니다.
 */

var HumanDesignSkill = {
    // 1. [금지 패턴 - AI Slop Anti-Patterns]
    forbiddenPatterns: [
        "사이버틱한 보라색/시안색 네온 그라데이션 남발 금지",
        "캔버스 전체를 어지럽게 채우는 과밀 배치 금지",
        "타이틀과 본문 크기 차이가 없는 난잡한 폰트 나열 금지",
        "배경과 텍스트의 대비(Contrast)가 부족하여 가독성이 떨어지는 색상 조합 금지"
    ],

    // 2. [인간 프로 디자이너 핵심 원칙]
    proRules: {
        // 충분하고 의도적인 안전 여백 (20% ~ 30% 호흡 공간)
        safeMarginPercent: 0.15,
        
        // 시각적 위계 질서 (제목은 압도적으로, 본문은 간결하게)
        hierarchyRatio: {
            heroToSub: 2.2,    // 대제목은 부제목의 약 2.2배 크기
            subToBody: 1.5     // 부제목은 본문의 약 1.5배 크기
        },
        
        // 감각적인 인간 디자이너 추천 컬러 팔레트 (Matte & Editorial)
        curatedPalettes: {
            nordicMinimal: ["#18181B", "#27272A", "#71717A", "#FAFAFA"],
            warmEditorial: ["#1F1D1A", "#8C7B6B", "#D9CDBF", "#F7F4EE"],
            boldDuoTone: ["#0B0C10", "#1F2833", "#C5C6C7", "#66FCF1"],
            softRetro: ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C"],
            freshStudio: ["#0D1B2A", "#1B263B", "#415A77", "#E0E1DD"]
        }
    }
};
