from django import forms


class formText(forms.Form): #Note that it is not inheriting from forms.ModelForm
    text = forms.CharField(max_length=1000000, widget=forms.TextInput(attrs={'class':'form_text'}))
    #All my attributes here


class SearchForm(forms.Form):
    query = forms.CharField(label='query', max_length=100)