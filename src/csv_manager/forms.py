from django import forms
from django.forms import ModelForm

from encodings.aliases import aliases
from models import CSV_Manager


class CSV_ManagerForm(forms.Form):
#class CSV_ManagerForm(ModelForm):
	title = forms.CharField()
	uri = forms.CharField()
	
	codec = forms.ChoiceField(widget=forms.Select)
    
	separator = forms.CharField()
	quotechar = forms.CharField()
	description = forms.CharField(widget=forms.Textarea)

	file = forms.FileField()

	class Meta:
		model = CSV_Manager
		fields = '__all__'
