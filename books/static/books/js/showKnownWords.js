var borderStyleSheet = document.createElement("style");
document.head.appendChild(borderStyleSheet);
borderStyleSheet.sheet.insertRule(".word[meta='known'] {color: #009900}", 0);

// disable rule
function resetStyle() {
borderStyleSheet.disabled = true;
}

// enable rule
function setStyle() {
borderStyleSheet.disabled = false;
}




