(function(){
  var list = document.getElementsByClassName("word");
  for(var i=0; i < list.length; i++){
     var a = list[i];
     a.addEventListener('mouseenter',createTip);
     a.addEventListener('mouseleave',cancelTip);
  }
  function createTip(ev){
    eventElement = this
    eventElement.setAttribute("tooltip", content);
    eventElement.classList.add("tooltip");

    var content = eventElement.textContent;

    var tooltipWrap = document.createElement("div"); //creates span
    tooltipWrap.className = 'tooltiptext'; //adds class

    var lastChild = eventElement.lastChild;//gets the first elem after body
    lastChild.parentNode.insertBefore(tooltipWrap, lastChild.nextSibling); //adds tt before elem

    $.ajax({
      url: '/ajax_word_data/',
      data: {
        'word': content
      },
      dataType: 'json',
      success: function (data) {

        if (data.is_in_dict) {
          zh_simpl = data.zh_simpl
          zh_trad = data.zh_trad
          pronunciation = data.pronunciation
          definitions = data.definitions
          hsk_level = data.hsk_level

          var tooltipWrapCharacter = document.createElement("p"); //creates p
          tooltipWrapCharacter.appendChild(document.createTextNode(`${zh_simpl} [${zh_trad}]`));
          tooltipWrapCharacter.className = 'tt-hanzi'
          tooltipWrap.appendChild(tooltipWrapCharacter); //add the text node to the newly created div.

          var tooltipWrapPronunciation = document.createElement("p"); //creates p
          tooltipWrapPronunciation.appendChild(document.createTextNode(`${pronunciation}`));
          tooltipWrapPronunciation.className = 'tt-fayin'
          tooltipWrap.appendChild(tooltipWrapPronunciation); //add the text node to the newly created div.


          for(var i=0; i < definitions.length; i++){
              var definition = definitions[i];
              var tooltipWrapDef = document.createElement("p"); //creates p
              tooltipWrapDef.appendChild(document.createTextNode(`- ${definition}`));
              tooltipWrapDef.className = 'tt-def'
              tooltipWrap.appendChild(tooltipWrapDef); //add the text node to the newly created div.
            }

          if (hsk_level != 0) {
              var tooltipWrapHSKLevel = document.createElement("p"); //creates p
              tooltipWrapHSKLevel.appendChild(document.createTextNode(`HSK ${hsk_level}`));
              tooltipWrapHSKLevel.className = 'tt-hsk'
              tooltipWrap.appendChild(tooltipWrapHSKLevel); //add the text node to the newly created div.
          }
        }
      }
    });
  }

  function cancelTip(ev){
    this.removeAttribute("tooltip");
    this.classList.remove("tooltip");
    document.querySelector(".tooltiptext").remove();
  }
})();