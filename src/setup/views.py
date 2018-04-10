from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext
from django.views import generic
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django import forms


from setup.models import Setup


# Language of UI
LANGUAGE_CHOICES = (
	('en', 'English'),
	('ar', 'Arabic'),
	('de', 'Deutsch (German)'),
	('it', 'Italian'),
	('pt', 'Portuguese'),
)


# Grammar / Stemming languages
LANGUAGES_CHOICES = (
	('en', 'English'),
	('ar', 'Arabic'),
	('de', 'Deutsch (German)'),
	('fa', 'Farsi (Persian)'),
	('fr', 'Francais (French)'),
	('it', 'Italian'),
	('nl', 'Dutch (Netherlands)'),
	('pt', 'Portuguese'),
	('es', 'Spanish'),
)


# OCR dictionaries
OCR_LANGUAGES_CHOICES = (
	('eng', 'English'),
	('ara', 'Arabic'),
	('deu', 'Deutsch (German)'),
	('deu-frak', 'Deutsch Frakturschrift (Old German)'),
	('far', 'Farsi (Persian)'),
	('hun', 'Hungarian'),
	('fra', 'Francais (French)'),
	('ita', 'Italian'),
	('nld', 'Dutch (Netherlands)'),
	('por', 'Portuguese'),
	('spa', 'Spanish'),
)


class SetupForm(ModelForm):

	class Meta:
		model = Setup
		exclude = ['language', 'languages', 'languages_force', 'ocr_languages']

		
	language = forms.ChoiceField(
		required=False,
		choices=LANGUAGE_CHOICES,
    )
		
	languages = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES,
    )

	languages_force = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES,
    )

	ocr_languages = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=OCR_LANGUAGES_CHOICES,
    )

class IndexView(generic.ListView):
	model = Setup

class DetailView(generic.DetailView):
	model = Setup

class UpdateView(generic.UpdateView):
	model = Setup


#
# Updated an setup
#

def update_setup(request, pk):

	setup = Setup.objects.get(pk=pk)
	
	if request.POST:
				
		form = SetupForm(request.POST, request.FILES, instance=setup)
		
		if form.is_valid():

			setup.language = form.cleaned_data['language']
			# manual handled MultipleChoiceField is saved comma separeted in a single CharField
			setup.languages = (',').join( form.cleaned_data['languages'] )
			setup.languages_force = (',').join( form.cleaned_data['languages_force'] )
			setup.ocr_languages = (',').join( form.cleaned_data['ocr_languages'] )

			form.save()

			return HttpResponseRedirect( reverse('setup:detail', args=[pk])) # Redirect after POST
		
			pass
	else:
		
		# The forms MultipleChoiceField is saved comma separeted in singe CharField,
		# so manual handling and turn over by form parameter initial
		language = setup.language
		languages = setup.languages.split(",")
		languages_force = setup.languages_force.split(",")
		ocr_languages = setup.ocr_languages.split(",")

		form = SetupForm( instance=setup, initial={ 'language': language, 'languages': languages, 'languages_force': languages_force, 'ocr_languages': ocr_languages } )

	return render(request, 'setup/setup_form.html', 
			{'form': form, 'setup': setup } )

