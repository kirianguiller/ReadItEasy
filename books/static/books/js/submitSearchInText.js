function searchInText__Validate(){
  formValue = document.getElementById('searchInText__input').value
  alert('Form submitted!' + formValue);
  var idBook = document.getElementById("id-book").textContent
  window.open('/books/mandarin/'+idBook+'/search/'+formValue, '_blank');
  return false;

}

function init(){
    document.getElementById('searchInText__form').onsubmit = searchInText__Validate;
}
window.onload = init;