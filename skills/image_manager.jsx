/**
 * Skill: Smart Image Placement & Clipping Mask
 * 로컬 또는 다운로드된 이미지를 캔버스에 정확한 좌표/크기로 배치하고 스마트 클리핑 마스크를 적용합니다.
 */
var ImageSkill = {
    // 캔버스에 이미지 파일 삽입 (Place)
    placeImage: function(imageFilePath, top, left, targetWidth, targetHeight) {
        var doc = app.activeDocument;
        var f = new File(imageFilePath);
        if (!f.exists) {
            return null;
        }

        var placed = doc.placedItems.add();
        placed.file = f;
        
        // 위치 지정 (left, top)
        placed.position = [left, top];

        // 크기 스케일링 (가로/세로 비율 유지 또는 타깃 크기 맞춤)
        if (targetWidth && targetHeight) {
            var scaleX = (targetWidth / placed.width) * 100;
            var scaleY = (targetHeight / placed.height) * 100;
            // Fill 비율 (더 큰 쪽에 맞춰 크롭)
            var finalScale = Math.max(scaleX, scaleY);
            placed.resize(finalScale, finalScale);
        } else if (targetWidth) {
            var s = (targetWidth / placed.width) * 100;
            placed.resize(s, s);
        }

        return placed;
    },

    // 둥근 사각형 클리핑 마스크 씌우기
    clipWithRoundedRect: function(placedItem, top, left, width, height, radius) {
        var doc = app.activeDocument;
        var grp = doc.groupItems.add();
        
        // 1. 마스크 패스 생성
        var mask = doc.pathItems.roundedRectangle(top, left, width, height, radius || 10, radius || 10);
        mask.stroked = false;
        mask.filled = true;

        // 2. 그룹에 이동 후 클립 활성화
        mask.moveToBeginning(grp);
        placedItem.moveToEnd(grp);
        grp.clipped = true;

        return grp;
    }
};
