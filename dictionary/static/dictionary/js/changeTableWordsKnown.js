function changeIsKnown(elt) {

    var word = elt.getAttribute("word");
    var childKnown = null;
    for (var i = 0; i < elt.childNodes.length; i++) {
    if (elt.childNodes[i].className == "known") {
      childKnown = elt.childNodes[i];
      break;
    }
}
console.log(childKnown)
    if (elt.getAttribute("is_known") == "False") {

      elt.setAttribute("is_known", "True")
      childKnown.textContent = "True"
      console.log(childKnown)
      $.ajax({
        url: '/dictionary/ajax_interact_known_word/',
        data: {
          'word': word,
          'action': 'add',
        },
        dataType: 'json',
        success: function (data) {
          console.log('the word : ' + word + ' was added to the known words list');
        }
      });

    } else {

      elt.setAttribute("is_known", "False")
      childKnown.textContent = "False"
      $.ajax({
        url: '/dictionary/ajax_interact_known_word/',
        data: {
          'word': word,
          'action': 'remove',
        },
        dataType: 'json',
        success: function (data) {
          console.log('the word : ' + word + ' was removed from the known words list');
        }
      });
    }
  }