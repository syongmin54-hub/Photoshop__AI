/**
 * Skill: Smart Typography & Scale Hierarchy
 * 타이포그래피 계층(헤드라인, 서브타이틀, 본문)과 가독성 최적화 스타일을 적용합니다.
 */
var TypographySkill = {
    // 텍스트 프레임에 폰트, 크기, 행간, 자간, 색상 일괄 적용
    applyStyle: function(textFrame, options) {
        if (!textFrame || !textFrame.textRange) return;
        var attr = textFrame.textRange.characterAttributes;
        
        if (options.fontSize) attr.size = options.fontSize;
        if (options.color) attr.fillColor = options.color;
        if (options.tracking) attr.tracking = options.tracking; // 자간
        if (options.leading) {
            attr.autoLeading = false;
            attr.leading = options.leading; // 행간
        }
        if (options.fontName) {
            try {
                attr.textFont = app.textFonts.getByName(options.fontName);
            } catch(e) {}
        }
    },
    
    // 타이포그래피 황금비율 스케일 (Base 16pt 기준)
    scales: {
        hero: 72,
        h1: 48,
        h2: 36,
        h3: 24,
        body: 16,
        caption: 12
    }
};
