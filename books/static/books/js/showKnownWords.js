var borderStyleSheet = document.createElement("style");
document.head.appendChild(borderStyleSheet);
borderStyleSheet.sheet.insertRule(".word[known='yes'] {color: #009900}", 0);

// disable rule
function resetStyle() {
borderStyleSheet.disabled = true;
}

// enable rule
function setStyle() {
borderStyleSheet.disabled = false;
}
// see existing stylesheets
console.log(document.styleSheets);




