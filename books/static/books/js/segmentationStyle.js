var segmentationMarginStyle = document.createElement("style");
document.head.appendChild(segmentationMarginStyle);
segmentationMarginStyle.sheet.insertRule(".word {margin-right: -5px}", 0);
setSegStyle();

// disable rule
function resetSegStyle() {
segmentationMarginStyle.disabled = false;
}

// enable rule
function setSegStyle() {
segmentationMarginStyle.disabled = true;
}