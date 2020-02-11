/*
var wordList = document.getElementsByClassName("word");
for(var i=0; i < wordList.length; i++){
    var wordSpan = wordList[i];
    wordSpan.setAttribute("content", wordSpan.textContent);
    */
/*wordSpan.setAttribute("known", "no");*//*

                    wordSpan.setAttribute("known", "yes");

    $.ajax({
        url: '/dictionary/getAJAX_user_known_word/',
        data: {
          'word': "了"
        },
        dataType: 'json',
        success: function (data) {
                console.log(data);

                if (data.is_known) {
                    wordSpan.setAttribute("known", "yes");
                    console.log('change ATTRIBUTE');
                    }
                else {
                wordSpan.setAttribute("known", "yes");
                }
                }

        })
}

*/
