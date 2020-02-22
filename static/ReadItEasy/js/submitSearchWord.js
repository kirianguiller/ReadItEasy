function searchWord__Validate(){
  formValue = document.getElementById('searchWord__input').value
//  alert('Form submitted!' + formValue);
  window.open('/dictionary/mandarin/'+formValue, '_blank');

  return false;

}

function init(){
    document.getElementById('searchWord__form').onsubmit = searchWord__Validate;
}
window.onload = init;