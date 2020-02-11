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
      var clickeElIsWord = clickInsideElement( e, "word" );
      if ( clickeElIsWord ) {
        content = clickeElIsWord.getAttribute('content')

        $.ajax({
          url: '/send_ajax_json/',
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
            var n_book_tokens = document.getElementById("n-book-tokens").textContent;
            var rel_book_freq = (1000000*data.book_freq/n_book_tokens).toFixed(0)
            document.getElementById("rel-book-freq").textContent = rel_book_freq;
            console.log(rel_book_freq)
            document.getElementById("rel-corpus-freq").textContent = data.corpus_freq;

            if (data.is_in_dict) {
              zh_simpl = data.zh_simpl
              zh_trad = data.zh_trad
              pronunciation = data.pronunciation
              definitions = data.definitions
              hsk_level = data.hsk_level


            }
          }
        });
      }
    });
  }

  init();
 })();