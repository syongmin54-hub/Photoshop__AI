/**
 * Skill: Color Harmony & Palette Generator
 * HEX 코드를 RGBColor 객체로 변환하고 트렌디한 디자인 팔레트를 제공합니다.
 */
var PaletteSkill = {
    // HEX 문자열("#FF5733" 또는 "FF5733")을 Adobe RGBColor로 변환
    hexToRgb: function(hex) {
        hex = hex.replace("#", "");
        if (hex.length === 3) {
            hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
        }
        var r = parseInt(hex.substring(0, 2), 16);
        var g = parseInt(hex.substring(2, 4), 16);
        var b = parseInt(hex.substring(4, 6), 16);
        
        var col = new RGBColor();
        col.red = r; col.green = g; col.blue = b;
        return col;
    },
    
    // 테마별 프리셋 팔레트
    themes: {
        oceanCool: ["#0F172A", "#1E293B", "#0284C7", "#38BDF8", "#F8FAFC"],
        vividSummer: ["#FFFBEB", "#F59E0B", "#EF4444", "#8B5CF6", "#1E1B4B"],
        darkNeon: ["#09090B", "#18181B", "#10B981", "#06B6D4", "#FAFAFA"],
        modernMinimal: ["#FFFFFF", "#F4F4F5", "#71717A", "#27272A", "#18181B"]
    }
};
