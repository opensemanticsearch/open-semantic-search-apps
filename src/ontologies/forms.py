from django import forms
from models import Ontologies

class OntologiesForm(forms.ModelForm):

	class Meta:
		model = Ontologies
