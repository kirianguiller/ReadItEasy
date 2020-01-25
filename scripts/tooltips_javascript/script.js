(function(){
  var list = document.getElementsByClassName("tooltip");
  console.log(document.getElementsByClassName("tooltip"));
  for(var i=0; i < list.length; i++){
     var a = list[i];
     console.log(a)
     if(1){
       a.addEventListener('mouseenter',createTip);
       a.addEventListener('mouseleave',cancelTip);
     }
    //console.log(a);
  }
  function createTip(ev){
/*      console.log(this.textContent);*/
      var content = this.textContent;
      this.setAttribute("tooltip", content);

      var tooltipWrap = document.createElement("div"); //creates span
      tooltipWrap.className = 'tooltiptext'; //adds class

      var tooltipWrapCharacter = document.createElement("p"); //creates span
      tooltipWrapCharacter.appendChild(document.createTextNode("老家 [老家]"));
      tooltipWrapCharacter.className = 'tt-hanzi'
      tooltipWrap.appendChild(tooltipWrapCharacter); //add the text node to the newly created div.

      var tooltipWrapPronunciation = document.createElement("p"); //creates span
      tooltipWrapPronunciation.appendChild(document.createTextNode("lao3 jia1"));
      tooltipWrapPronunciation.className = 'tt-fayin'
      tooltipWrap.appendChild(tooltipWrapPronunciation); //add the text node to the newly created div.

      var tooltipWrapDef = document.createElement("p"); //creates span
      tooltipWrapDef.appendChild(document.createTextNode("- native place"));
      tooltipWrapDef.className = 'tt-def'
      tooltipWrap.appendChild(tooltipWrapDef); //add the text node to the newly created div.

      var tooltipWrapDef = document.createElement("p"); //creates span
      tooltipWrapDef.appendChild(document.createTextNode("- place of origin"));
      tooltipWrapDef.className = 'tt-def'
      tooltipWrap.appendChild(tooltipWrapDef); //add the text node to the newly created div.



      var lastChild = this.lastChild;//gets the first elem after body
     /* var lastChild = document.body.lastChild;//gets the first elem after body*/

      lastChild.parentNode.insertBefore(tooltipWrap, lastChild.nextSibling); //adds tt before elem
  }

  function cancelTip(ev){
      this.removeAttribute("tooltip");
      document.querySelector(".tooltiptext").remove();
  }
})();
