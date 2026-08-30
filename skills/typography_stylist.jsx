/**
 * Skill: Smart Typography & Real Installed Korean Font Mapper
 * 시스템에 설치된 실제 PostScript 폰트명을 정확하게 매핑하여 서체 깨짐 및 기본 폰트 폴백을 방지합니다.
 */
var TypographySkill = {
    // 실제 검증된 시스템 한글 폰트 매핑 테이블 (일러스트레이터 정식 PostScriptName)
    koreanFonts: {
        // 명조 / 바탕 계열 (한의원, 에디토리얼, 감성, 신뢰)
        serif: {
            bold: "KoPubBatangBold",
            regular: "KoPubBatangMedium",
            light: "KoPubBatangLight",
            nanumBold: "NanumMyeongjoBold",
            nanumRegular: "NanumMyeongjo",
            notoBold: "NotoSerifKR-Bold",
            notoRegular: "NotoSerifKR-Regular"
        },
        // 모던 고딕 / 산세리프 계열 (깔끔함, 현대적 클리닉, IT, 비즈니스)
        sans: {
            neoBold: "NanumSquareNeoTTF-cBd",
            neoRegular: "NanumSquareNeoTTF-bRg",
            squareBold: "NanumSquareB",
            squareRegular: "NanumSquareR",
            kopubBold: "KoPubDotumBold",
            kopubRegular: "KoPubDotumMedium",
            notoBold: "NotoSansKR-Bold",
            notoRegular: "NotoSansKR-Regular"
        },
        // 타이틀 / 강조 / 배너용 볼드
        display: {
            blackHanSans: "BlackHanSans-Regular",
            tmonMonsori: "TmonMonsoriOTFBlack",
            heavySquare: "NanumSquareNeoTTF-eHv"
        }
    },

    // 안전하게 폰트 적용
    setFont: function(textFrame, postScriptName) {
        if (!textFrame || !textFrame.textRange) return false;
        try {
            var f = app.textFonts.getByName(postScriptName);
            textFrame.textRange.characterAttributes.textFont = f;
            return true;
        } catch(e) {
            return false;
        }
    },

    // 텍스트 프레임에 폰트, 크기, 행간, 자간 일괄 적용
    applyStyle: function(textFrame, options) {
        if (!textFrame || !textFrame.textRange) return;
        var attr = textFrame.textRange.characterAttributes;
        
        if (options.fontSize) attr.size = options.fontSize;
        if (options.color) attr.fillColor = options.color;
        if (options.tracking !== undefined) attr.tracking = options.tracking;
        if (options.leading) {
            attr.autoLeading = false;
            attr.leading = options.leading;
        }
        if (options.fontName) {
            this.setFont(textFrame, options.fontName);
        }
    }
};
