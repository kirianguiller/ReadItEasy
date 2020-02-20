function forceTokenize(word) {
        $.ajax({
        url: '/ajax_change_tokenization/',
        data: {
          'word': word,
          'action': 'separate'
        },
        dataType: 'json',
        success: function (data) {
                console.log("the word "+word+" will now be tokenized");
                location.reload();
        }
    })
}


function validate(){
  formValue = document.getElementById('changeTokenization__input').value
  alert('Form submitted!' + formValue);

  forceTokenize(formValue)
  return false;

}

function init(){
    document.getElementById('changeTokenization__form').onsubmit = validate;
}
window.onload = init;