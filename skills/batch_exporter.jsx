/**
 * Skill: Smart Export Manager (PNG / SVG / PDF)
 * 현재 아트보드 또는 선택 요소를 고해상도 웹/인쇄용 포맷으로 내보냅니다.
 */
var ExportSkill = {
    // PNG 24 고해상도 내보내기
    exportPng24: function(destFilePath, scalePercent) {
        var doc = app.activeDocument;
        var file = new File(destFilePath);
        var options = new ExportOptionsPNG24();
        options.antiAliasing = true;
        options.transparency = true;
        options.artBoardClipping = true;
        if (scalePercent) {
            options.horizontalScale = scalePercent;
            options.verticalScale = scalePercent;
        }
        doc.exportFile(file, ExportType.PNG24, options);
        return file.fsName;
    },
    
    // SVG 벡터 내보내기
    exportSvg: function(destFilePath) {
        var doc = app.activeDocument;
        var file = new File(destFilePath);
        var options = new ExportOptionsSVG();
        options.embedRasterImages = true;
        options.fontSubsetting = SVGFontSubsetting.GLYPHSUSED;
        doc.exportFile(file, ExportType.SVG, options);
        return file.fsName;
    }
};
