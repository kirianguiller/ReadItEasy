var wordList = document.getElementsByClassName("word");

for(var i=0; i < wordList.length; i++){
 var wordSpan = wordList[i];
 console.log(wordSpan);
 wordSpan.setAttribute("known", "no")
 wordSpan.setAttribute("content", wordSpan.textContent)

 if(wordSpan === "小镇"){
    console.log(wordSpan)
 }
//console.log(a);
}
