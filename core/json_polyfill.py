# ExtendScript $.global.JSON Polyfill for Adobe Photoshop & Illustrator
EXTENDSCRIPT_JSON_POLYFILL = """
if (typeof $.global.JSON !== 'object' || !$.global.JSON.stringify) {
    $.global.JSON = {};
    $.global.JSON.stringify = function(obj) {
        if (obj === null || obj === undefined) return "null";
        if (typeof obj === "number" || typeof obj === "boolean") return String(obj);
        if (typeof obj === "string") {
            return '"' + obj.replace(/\\\\/g, '\\\\\\\\').replace(/"/g, '\\\\"').replace(/\\n/g, '\\\\n').replace(/\\r/g, '\\\\r').replace(/\\t/g, '\\\\t') + '"';
        }
        if (obj instanceof Array) {
            var arr = [];
            for (var i = 0; i < obj.length; i++) {
                arr.push($.global.JSON.stringify(obj[i]));
            }
            return "[" + arr.join(",") + "]";
        }
        if (typeof obj === "object") {
            var pairs = [];
            for (var k in obj) {
                if (obj.hasOwnProperty(k)) {
                    pairs.push('"' + k + '":' + $.global.JSON.stringify(obj[k]));
                }
            }
            return "{" + pairs.join(",") + "}";
        }
        return '""';
    };
    $.global.JSON.parse = function(text) {
        return eval('(' + text + ')');
    };
}
var JSON = $.global.JSON;
"""
