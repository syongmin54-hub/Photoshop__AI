/**
 * Skill: Smart Auto Layout & Padding
 * 요소의 크기 변화에 맞춰 배경 박스를 감싸거나 요소 간격을 균등하게 자동 배치합니다.
 */
var AutoLayoutSkill = {
    // 텍스트 프레임 주위에 균일한 패딩을 가진 배경 박스를 생성/조정
    wrapWithPadding: function(textFrame, padTop, padRight, padBottom, padLeft, fillColor) {
        var doc = app.activeDocument;
        var tPos = textFrame.position; // [left, top]
        var tW = textFrame.width;
        var tH = textFrame.height;
        
        var boxTop = tPos[1] + padTop;
        var boxLeft = tPos[0] - padLeft;
        var boxW = tW + padLeft + padRight;
        var boxH = tH + padTop + padBottom;
        
        var bg = doc.pathItems.rectangle(boxTop, boxLeft, boxW, boxH);
        if (fillColor) {
            bg.fillColor = fillColor;
            bg.stroked = false;
        }
        // 텍스트 뒤로 배치
        bg.zOrder(ZOrderMethod.SENDTOBACK);
        return bg;
    },
    
    // 여러 아이템을 수직/수평 균등 간격으로 분배
    distributeItems: function(items, spacing, isVertical) {
        var currentPos = isVertical ? items[0].position[1] : items[0].position[0];
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            if (isVertical) {
                item.position = [item.position[0], currentPos];
                currentPos -= (item.height + spacing);
            } else {
                item.position = [currentPos, item.position[1]];
                currentPos += (item.width + spacing);
            }
        }
    }
};
