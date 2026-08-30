/**
 * Skill: Multi-page Artboards Manager (Card News, Portfolio, Brochure)
 * 카드뉴스 여러 장, 포트폴리오 다중 페이지, 브로슈어 슬라이드를 그리드로 생성하고 관리합니다.
 */

var MultiPageSkill = {
    // 다중 아트보드(페이지) 일괄 생성 (pageCount: 페이지 수, width, height, spacing, cols)
    createMultiPages: function(pageCount, width, height, spacing, cols) {
        var doc = app.activeDocument;
        spacing = spacing || 50;
        cols = cols || Math.min(pageCount, 5);

        // 첫 번째 기본 아트보드 크기 조절
        var firstAb = doc.artboards[0];
        firstAb.artboardRect = [0, height, width, 0];
        firstAb.name = "Page 1";

        // 2번째 페이지부터 순차 생성 및 배치
        for (var i = 1; i < pageCount; i++) {
            var colIdx = i % cols;
            var rowIdx = Math.floor(i / cols);

            var left = colIdx * (width + spacing);
            var top = -(rowIdx * (height + spacing)) + height;
            var right = left + width;
            var bottom = top - height;

            var newAb = doc.artboards.add([left, top, right, bottom]);
            newAb.name = "Page " + (i + 1);
        }

        return doc.artboards.length;
    },

    // 특정 페이지(아트보드)의 좌상단 시작 좌표 반환
    getPageOrigin: function(pageIndex) {
        var doc = app.activeDocument;
        if (pageIndex >= doc.artboards.length) pageIndex = 0;
        var r = doc.artboards[pageIndex].artboardRect;
        return {
            left: r[0],
            top: r[1],
            width: Math.abs(r[2] - r[0]),
            height: Math.abs(r[1] - r[3])
        };
    }
};
