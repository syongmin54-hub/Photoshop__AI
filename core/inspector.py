import json
from typing import Any, Dict, List
from core.bridge_ai import IllustratorBridge
from core.bridge_ps import PhotoshopBridge


class DocumentInspector:
    """Extracts rich, decomposed DOM state (Artboards, Text, Images, Shapes) like HWPX element parser."""

    ILLUSTRATOR_DEEP_INSPECT_JSX = """
if (app.documents.length === 0) {
    return JSON.stringify({"has_document": false, "message": "열린 문서가 없습니다."});
}

var doc = app.activeDocument;

// Helper: RGB to Hex
function rgbToHex(color) {
    if (!color) return "#000000";
    if (color.typename === "RGBColor") {
        var r = color.red.toString(16); if (r.length === 1) r = "0" + r;
        var g = color.green.toString(16); if (g.length === 1) g = "0" + g;
        var b = color.blue.toString(16); if (b.length === 1) b = "0" + b;
        return "#" + r + g + b;
    }
    return "#000000";
}

var result = {
    "has_document": true,
    "app": "Illustrator",
    "name": doc.name,
    "colorMode": (doc.documentColorSpace == DocumentColorSpace.RGB) ? "RGB" : "CMYK",
    "artboards": [],
    "textElements": [],
    "imageElements": [],
    "shapeElements": []
};

// 1. Deconstruct all Artboards (Multi-page support)
for (var a = 0; a < doc.artboards.length; a++) {
    var ab = doc.artboards[a];
    var rect = ab.artboardRect; // [left, top, right, bottom]
    result.artboards.push({
        "index": a,
        "name": ab.name,
        "left": Math.round(rect[0]),
        "top": Math.round(rect[1]),
        "right": Math.round(rect[2]),
        "bottom": Math.round(rect[3]),
        "width": Math.round(Math.abs(rect[2] - rect[0])),
        "height": Math.round(Math.abs(rect[1] - rect[3]))
    });
}

// 2. Deconstruct all Text Frames (Typography & Content)
for (var t = 0; t < doc.textFrames.length; t++) {
    var tf = doc.textFrames[t];
    var txt = tf.contents.replace(/\\r/g, '\\n').trim();
    if (txt.length === 0) continue;

    var tfData = {
        "id": t,
        "content": txt,
        "left": Math.round(tf.position[0]),
        "top": Math.round(tf.position[1]),
        "width": Math.round(tf.width),
        "height": Math.round(tf.height),
        "lines": txt.split('\\n').length
    };

    try {
        if (tf.textRange && tf.textRange.characterAttributes) {
            var attr = tf.textRange.characterAttributes;
            tfData.fontSize = attr.size;
            tfData.tracking = attr.tracking;
            tfData.autoLeading = attr.autoLeading;
            tfData.leading = attr.leading;
            if (attr.textFont) {
                tfData.fontPostScript = attr.textFont.name;
                tfData.fontFamily = attr.textFont.family;
            }
            if (attr.fillColor) {
                tfData.color = rgbToHex(attr.fillColor);
            }
        }
    } catch(e) {}

    result.textElements.push(tfData);
}

// 3. Deconstruct all Placed/Raster Images
for (var p = 0; p < doc.placedItems.length; p++) {
    var pi = doc.placedItems[p];
    var imgData = {
        "id": p,
        "type": "PlacedItem",
        "left": Math.round(pi.position[0]),
        "top": Math.round(pi.position[1]),
        "width": Math.round(pi.width),
        "height": Math.round(pi.height),
        "filePath": pi.file ? pi.file.fsName : "embedded"
    };
    result.imageElements.push(imgData);
}

for (var r = 0; r < doc.rasterItems.length; r++) {
    var ri = doc.rasterItems[r];
    result.imageElements.push({
        "id": r + doc.placedItems.length,
        "type": "RasterItem",
        "left": Math.round(ri.position[0]),
        "top": Math.round(ri.position[1]),
        "width": Math.round(ri.width),
        "height": Math.round(ri.height)
    });
}

// 4. Deconstruct Structural Shapes / Cards / Backgrounds
for (var s = 0; s < Math.min(doc.pathItems.length, 30); s++) {
    var pi = doc.pathItems[s];
    var shapeData = {
        "id": s,
        "left": Math.round(pi.position[0]),
        "top": Math.round(pi.position[1]),
        "width": Math.round(pi.width),
        "height": Math.round(pi.height),
        "filled": pi.filled,
        "stroked": pi.stroked
    };
    if (pi.filled && pi.fillColor) shapeData.fillColor = rgbToHex(pi.fillColor);
    if (pi.stroked && pi.strokeColor) shapeData.strokeColor = rgbToHex(pi.strokeColor);
    result.shapeElements.push(shapeData);
}

return JSON.stringify(result);
"""

    PHOTOSHOP_DEEP_INSPECT_JSX = """
if (app.documents.length === 0) {
    return JSON.stringify({"has_document": false, "message": "열린 문서가 없습니다."});
}

var doc = app.activeDocument;
var result = {
    "has_document": true,
    "app": "Photoshop",
    "name": doc.name,
    "width": doc.width.value,
    "height": doc.height.value,
    "resolution": doc.resolution,
    "mode": doc.mode.toString(),
    "textElements": [],
    "layerElements": []
};

function scanPsLayers(parent, pathPrefix) {
    for (var i = 0; i < parent.layers.length; i++) {
        var layer = parent.layers[i];
        var fullPath = pathPrefix ? (pathPrefix + "/" + layer.name) : layer.name;
        
        var lInfo = {
            "name": layer.name,
            "path": fullPath,
            "visible": layer.visible,
            "opacity": Math.round(layer.opacity),
            "kind": layer.typename
        };

        if (layer.typename === "ArtLayer" && layer.kind === LayerKind.TEXT) {
            try {
                var tItem = layer.textItem;
                result.textElements.push({
                    "layerName": layer.name,
                    "content": tItem.contents,
                    "fontSize": Math.round(tItem.size.value),
                    "font": tItem.font,
                    "color": tItem.color.rgb.hexValue ? ("#" + tItem.color.rgb.hexValue) : ""
                });
            } catch(e) {}
        }

        if (layer.typename === "LayerSet") {
            scanPsLayers(layer, fullPath);
        } else {
            result.layerElements.push(lInfo);
        }
    }
}

scanPsLayers(doc, "");
return JSON.stringify(result);
"""

    @classmethod
    def inspect_illustrator(cls, bridge: IllustratorBridge) -> Dict[str, Any]:
        """Inspect detailed decomposed elements from Illustrator."""
        res = bridge.execute_jsx(cls.ILLUSTRATOR_DEEP_INSPECT_JSX)
        if res.get("success") and isinstance(res.get("result"), dict):
            return res["result"]
        return res

    @classmethod
    def inspect_photoshop(cls, bridge: PhotoshopBridge) -> Dict[str, Any]:
        """Inspect detailed decomposed elements from Photoshop."""
        res = bridge.execute_jsx(cls.PHOTOSHOP_DEEP_INSPECT_JSX)
        if res.get("success") and isinstance(res.get("result"), dict):
            return res["result"]
        return res
