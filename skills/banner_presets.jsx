/**
 * Skill: Real-world Design Presets (Banner, Card News, Poster, Banner Banner)
 * 실무 규격 자동 변환 헬퍼 (mm -> pt, px -> pt)
 */

var PresetSkill = {
    // mm 단위를 pt 단위로 변환 (1mm = 2.834645 pt)
    mmToPt: function(mm) {
        return mm * 2.834645;
    },

    // 표준 규격 프리셋
    sizes: {
        // 디지털 & SNS
        cardNewsSquare: { w: 1080, h: 1080, name: "Instagram Card News (1:1)" },
        cardNewsPortrait: { w: 1080, h: 1350, name: "Instagram Portrait (4:5)" },
        storyReels: { w: 1080, h: 1920, name: "Instagram Story / Reels (9:16)" },
        youtubeThumbnail: { w: 1280, h: 720, name: "YouTube Thumbnail (HD)" },
        webHeroBanner: { w: 1920, h: 1080, name: "Web Full Banner (FHD)" },

        // 오프라인 인쇄 & 현수막
        xBannerVertical: { w: 600 * 2.834645, h: 1800 * 2.834645, name: "X-Banner (600x1800mm)" },
        outdoorBanner: { w: 5000 * 2.834645 * 0.1, h: 900 * 2.834645 * 0.1, name: "Street Banner 1:10 scale (5000x900mm)" },
        a4Landscape: { w: 841.89, h: 595.28, name: "A4 Landscape" },
        a4Portrait: { w: 595.28, h: 841.89, name: "A4 Portrait" },
        a3Portrait: { w: 841.89, h: 1190.55, name: "A3 Poster" }
    }
};
