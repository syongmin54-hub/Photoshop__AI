/**
 * Skill: Portfolio & Complex Photo Grid Layout
 * 여러 장의 복잡한 사진이 들어가는 포트폴리오, 룩북, 매거진 갤러리 그리드를 생성합니다.
 */

var PortfolioSkill = {
    // N분할 사진 그리드 프레임 생성 (Masonry & Uniform Grid)
    createPhotoGrid: function(originLeft, originTop, totalWidth, totalHeight, rows, cols, gap, radius) {
        var doc = app.activeDocument;
        gap = gap || 16;
        radius = radius || 12;

        var cellW = (totalWidth - (gap * (cols - 1))) / cols;
        var cellH = (totalHeight - (gap * (rows - 1))) / rows;
        var frames = [];

        for (var r = 0; r < rows; r++) {
            for (var c = 0; c < cols; c++) {
                var left = originLeft + c * (cellW + gap);
                var top = originTop - r * (cellH + gap);

                var box = doc.pathItems.roundedRectangle(top, left, cellW, cellH, radius, radius);
                box.fillColor = LayoutSystem ? LayoutSystem.hexToRgb ? LayoutSystem.hexToRgb('#222222') : box.fillColor : box.fillColor;
                box.stroked = false;

                frames.push({
                    row: r,
                    col: c,
                    left: left,
                    top: top,
                    width: cellW,
                    height: cellH,
                    box: box
                });
            }
        }
        return frames;
    }
};
