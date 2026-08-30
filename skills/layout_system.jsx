/**
 * Skill: Illustrator Absolute Layout & High-Contrast Guardrails
 * 1. Y좌표는 반드시 doc.height - Y_offset (양수) 공식을 사용합니다. (음수 Y좌표 절대 금지)
 * 2. 다크 배경에는 무조건 선명한 화이트/골드(#FFFFFF, #D4AF37) 텍스트를 사용하여 묻힘을 방지합니다.
 */

var LayoutSystem = {
    // 캔버스 상단(Top) 기준 Y좌표 변환 (0 = 상단 끝, 100 = 상단에서 100pt 아래)
    topY: function(offsetFromTop) {
        var doc = app.activeDocument;
        return doc.height - offsetFromTop;
    },

    // 안전한 텍스트 위치 지정
    setTextPos: function(textFrame, left, offsetFromTop) {
        var doc = app.activeDocument;
        textFrame.position = [left, doc.height - offsetFromTop];
    },

    // 안전한 사각형 박스 생성
    addRect: function(left, offsetFromTop, width, height, radius) {
        var doc = app.activeDocument;
        var top = doc.height - offsetFromTop;
        if (radius) {
            return doc.pathItems.roundedRectangle(top, left, width, height, radius, radius);
        }
        return doc.pathItems.rectangle(top, left, width, height);
    },

    // 기존 캔버스 전체 초기화 (새 레이아웃 생성 시 중복 겹침 방지)
    clearCanvas: function() {
        var doc = app.activeDocument;
        while (doc.pathItems.length > 0) { doc.pathItems[0].remove(); }
        while (doc.placedItems.length > 0) { doc.placedItems[0].remove(); }
        while (doc.groupItems.length > 0) { doc.groupItems[0].remove(); }
        while (doc.textFrames.length > 0) { doc.textFrames[0].remove(); }
    }
};
