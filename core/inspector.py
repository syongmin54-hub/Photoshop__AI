import json
from typing import Any, Dict
from core.bridge_ai import IllustratorBridge
from core.bridge_ps import PhotoshopBridge


class DocumentInspector:
    """Extracts rich DOM state (layers, text frames, artboards, dimensions) as JSON."""

    ILLUSTRATOR_INSPECT_JSX = """
if (app.documents.length === 0) {
    return JSON.stringify({"has_document": false, "message": "열린 문서가 없습니다."});
}

var doc = app.activeDocument;
var ab = doc.artboards[doc.artboards.getActiveArtboardIndex()];
var rect = ab.artboardRect;

var result = {
    "has_document": true,
    "app": "Illustrator",
    "name": doc.name,
    "width": Math.abs(rect[2] - rect[0]),
    "height": Math.abs(rect[1] - rect[3]),
    "colorMode": (doc.documentColorSpace == DocumentColorSpace.RGB) ? "RGB" : "CMYK",
    "layers": [],
    "textFrames": []
};

for (var i = 0; i < doc.layers.length; i++) {
    var l = doc.layers[i];
    result.layers.push({
        "index": i,
        "name": l.name,
        "visible": l.visible,
        "locked": l.locked,
        "opacity": l.opacity
    });
}

for (var t = 0; t < doc.textFrames.length; t++) {
    var tf = doc.textFrames[t];
    var tfInfo = {
        "index": t,
        "contents": tf.contents,
        "width": Math.round(tf.width),
        "height": Math.round(tf.height)
    };
    try {
        tfInfo.position = [Math.round(tf.position[0]), Math.round(tf.position[1])];
        if (tf.textRange && tf.textRange.characterAttributes) {
            tfInfo.fontSize = tf.textRange.characterAttributes.size;
        }
    } catch(err) {}
    result.textFrames.push(tfInfo);
}

return JSON.stringify(result);
"""

    @classmethod
    def inspect_illustrator(cls, bridge: IllustratorBridge) -> Dict[str, Any]:
        """Inspect current active Illustrator document."""
        res = bridge.execute_jsx(cls.ILLUSTRATOR_INSPECT_JSX)
        if res.get("success") and isinstance(res.get("result"), dict):
            return res["result"]
        return res

    @classmethod
    def inspect_photoshop(cls, bridge: PhotoshopBridge) -> Dict[str, Any]:
        """Inspect current active Photoshop document."""
        res = bridge.execute_jsx(cls.PHOTOSHOP_INSPECT_JSX)
        if res.get("success") and isinstance(res.get("result"), dict):
            return res["result"]
        return res
