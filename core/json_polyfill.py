# Complete ES3 Polyfills for Adobe ExtendScript
EXTENDSCRIPT_JSON_POLYFILL = """
// 1. Array Polyfills
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function(item, from) {
        var len = this.length;
        var i = (from < 0) ? Math.max(0, len + from) : (from || 0);
        for (; i < len; i++) {
            if (this[i] === item) return i;
        }
        return -1;
    };
}
if (!Array.prototype.forEach) {
    Array.prototype.forEach = function(fn, scope) {
        for (var i = 0, len = this.length; i < len; ++i) {
            if (i in this) {
                fn.call(scope, this[i], i, this);
            }
        }
    };
}

// 2. String Polyfills
if (!String.prototype.trim) {
    String.prototype.trim = function() {
        return this.replace(/^\\s+|\\s+$/g, '');
    };
}

// 3. JSON Polyfill
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
