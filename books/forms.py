from django import forms


class formText(forms.Form): #Note that it is not inheriting from forms.ModelForm
    text = forms.CharField(max_length=1000000, widget=forms.TextInput(attrs={'class':'form_text'}))
    #All my attributes here