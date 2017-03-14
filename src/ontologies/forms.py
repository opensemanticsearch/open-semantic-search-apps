from django import forms
from models import Ontologies



class OntologiesForm(forms.ModelForm):
#	title = forms.CharField()
#	uri = forms.CharField()
	
#	description = forms.CharField(widget=forms.Textarea)

#	file = forms.FileField()


	class Meta:
		model = Ontologies
