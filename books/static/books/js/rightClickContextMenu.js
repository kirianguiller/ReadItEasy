(function() {

  "use strict";

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

  function getPosition(e) {
    var posx = 0;
    var posy = 0;

    if (!e) var e = window.event;

    if (e.pageX || e.pageY) {
      posx = e.pageX;
      posy = e.pageY;
    } else if (e.clientX || e.clientY) {
      posx = e.clientX + document.body.scrollLeft +
                         document.documentElement.scrollLeft;
      posy = e.clientY + document.body.scrollTop +
                         document.documentElement.scrollTop;
    }
    return {
      x: posx,
      y: posy
    }
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
  var contextMenuItemClassName = "context-menu__item";
  var contextMenuLinkClassName = "context-menu__link";
  var contextMenuActive = "context-menu--active";

  var clickableClassName = "word";
  var clickableInContext;

  var clickCoords;
  var clickCoordsX;
  var clickCoordsY;

  var menu = document.querySelector("#context-menu");
  var menuItems = menu.querySelectorAll(".context-menu__item");
  var menuState = 0;
  var menuWidth;
  var menuHeight;
  var menuPosition;
  var menuPositionX;
  var menuPositionY;

  var windowWidth;
  var windowHeight;

  var clickedAction;
  var clickedWordSpan;
  var clickedWordContentAttr;

  /**
   * Initialise our application's code.
   */
  function init() {
    contextListener();
    clickListener();
    keyupListener();
    resizeListener();
  }

  /**
   * Listens for contextmenu events.
   */

  function contextListener() {
    document.addEventListener( "contextmenu", function(e) {
      clickableInContext = clickInsideElement( e, clickableClassName );

      if ( clickableInContext ) {
        e.preventDefault();
        toggleMenuOn();
        positionMenu(e);
      } else {
        clickableInContext = null;
        toggleMenuOff();
      }
    });
  }


  /**
   * Listens for click events.
   */
  function clickListener() {
    document.addEventListener( "click", function(e) {
      var clickeElIsLink = clickInsideElement( e, contextMenuLinkClassName );

      if ( clickeElIsLink ) {
        e.preventDefault();
        menuItemListener( clickeElIsLink );
      }
      else {
        var button = e.which || e.button;
        if ( button === 1 ) {
          toggleMenuOff();
        }
      }
    });
  }

  /**
   * Listens for keyup events.
   */
  function keyupListener() {
    window.onkeyup = function(e) {
      if ( e.keyCode === 27 ) {
        toggleMenuOff();
      }
    }
  }

  /**
   * Listens for windows resize events.
   */
  function resizeListener() {
    window.addEventListener("resize", function(e) {
      toggleMenuOff();
    });
  }

  function menuItemListener( link ) {
    clickedAction = link.getAttribute("data-action")
    clickedWordSpan = clickableInContext
    clickedWordContentAttr = clickedWordSpan.getAttribute('content')
    console.log( "Word content - " +clickableInContext.textContent +", Action - " + link.getAttribute("data-action"));
    toggleMenuOff();

    if (clickedAction === 'Add') {
      addToKnownWords(clickedWordContentAttr);
      var wordList = document.querySelectorAll(`[content="${clickedWordContentAttr}"]`);
      for(var i=0; i < wordList.length; i++){
        wordList[i].setAttribute("meta", "known");
      }
    }
    if (clickedAction === 'Remove') {
      removeFromKnownWords(clickedWordContentAttr);
      var wordList = document.querySelectorAll(`[content="${clickedWordContentAttr}"]`);
      for(var i=0; i < wordList.length; i++){
        wordList[i].setAttribute("meta", "unknown");
      }
    }

    if (clickedAction === 'Info') {
      console.log('GET INFO');
      window.open('/dictionary/mandarin/'+clickedWordContentAttr, '_blank');
    }

    if (clickedAction === 'Tokenize') {
      console.log('tokenize', clickedWordContentAttr);
      forceTokenize(clickedWordContentAttr)
    }

    if (clickedAction === 'Search') {
      console.log('GET INFO');
      window.open('/books/mandarin/'+idBook+'/search/'+clickedWordContentAttr, '_blank');
    }

    if (clickedAction === 'Copy') {
      console.log('copy', clickedWordContentAttr);
      window.prompt("Copy to clipboard: Ctrl+C, Enter", clickedWordContentAttr);
/*        var copyText = document.getElementById("myInput");
  copyText.select();*/
    }

  }

  /**
   * Turns the custom context menu on.
   */
  function toggleMenuOn() {
    if ( menuState !== 1 ) {
      menuState = 1;
      menu.classList.add( contextMenuActive );
    }
  }

  function toggleMenuOff() {
    if ( menuState !== 0 ) {
      menuState = 0;
      menu.classList.remove( contextMenuActive );
    }
  }

  function addToKnownWords(word) {
    $.ajax({
      url: '/dictionary/ajax_interact_known_word/',
      data: {
        'word': word,
        'action': 'add',
      },
      dataType: 'json',
      success: function (data) {
      console.log('WORD ADDED');
      }
    })
  }

    function removeFromKnownWords(word) {
    $.ajax({
      url: '/dictionary/ajax_interact_known_word/',
      data: {
        'word': word,
        'action': 'remove',
      },
      dataType: 'json',
      success: function (data) {
      console.log('WORD REMOVED');
      }
    })
  }

  function positionMenu(e) {
    clickCoords = getPosition(e);
    clickCoordsX = clickCoords.x;
    clickCoordsY = clickCoords.y;

    menuWidth = menu.offsetWidth + 4;
    menuHeight = menu.offsetHeight + 4;

    windowWidth = window.innerWidth;
    windowHeight = window.innerHeight;


    if ( (windowWidth - clickCoordsX) < menuWidth ) {
      menu.style.left = windowWidth - menuWidth + "px";
    } else {
      menu.style.left = clickCoordsX + "px";
    }

    if ( (windowHeight - clickCoordsY) < menuHeight ) {
      menu.style.top = windowHeight - menuHeight + "px";
      menu.style.top = clickCoordsY - 60  + "px";
    } else {
      menu.style.top = clickCoordsY + "px";
      menu.style.top = clickCoordsY - 60  + "px";

    }
  }  /**
   * Run the app.
   */
  init();

})();
