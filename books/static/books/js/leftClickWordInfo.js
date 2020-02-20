(function() {
  "use strict";
  console.log('Start Script');

  ///////////////////////////////////////
  ///////////////////////////////////////
  //
  // H E L P E R    F U N C T I O N S
  //
  ///////////////////////////////////////
  ///////////////////////////////////////

  /**
   * Some helper functions here.
   */
  function clickInsideElement( e, className ) {
    var el = e.srcElement || e.target;

    if ( el.classList.contains(className) ) {
      return el;
    } else {
      while ( el = el.parentNode ) {
        if ( el.classList && el.classList.contains(className) ) {
          return el;
        }
      }
    }
  return false;
  }


  ///////////////////////////////////////
  ///////////////////////////////////////
  //
  // C O R E    F U N C T I O N S
  //
  ///////////////////////////////////////
  ///////////////////////////////////////

  /**
   * Variables.
   */

  var idBook = document.getElementById("id-book").textContent
  var content
  var clickeElIsWord
  /**
   * Initialise our application's code.
   */

  function init() {
    leftClickListener();
  }


  /**
   * Listens for LeftClick events.
   */

  function leftClickListener() {
    document.addEventListener( "click", function(e) {
      clickeElIsWord = clickInsideElement( e, "word" );
      if ( clickeElIsWord ) {
        content = clickeElIsWord.getAttribute('content')

        $.ajax({
          url: '/ajax_word_data/',
          data: {
            'word': content,
            'is_freqs': 'True',
            'id_book': idBook,
          },
          dataType: 'json',
          success: function (data) {

            document.getElementById("wi-simp").textContent = content;
            document.getElementById("book-rank").textContent = data.book_rank;
            document.getElementById("corpus-rank").textContent = data.corpus_rank;
            document.getElementById("abs-book-freq").textContent = data.book_freq;
            document.getElementById("rel-book-freq").textContent = data.book_rel_freq;
            document.getElementById("rel-corpus-freq").textContent = data.corpus_freq;

            if (data.is_in_dict) {
              zh_simpl = data.zh_simpl
              zh_trad = data.zh_trad
              pronunciation = data.pronunciation
              definitions = data.definitions
              hsk_level = data.hsk_level
              document.getElementById("wi-trad").textContent = zh_trad;
              document.getElementById("wi-pron").textContent = pronunciation;
              document.getElementById("wi-hsk").textContent = hsk_level;

            }
          }
        });
      }
    });
  }

  init();
 })();