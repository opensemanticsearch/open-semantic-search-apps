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
	('cz', 'Czech'),
	('de', 'Deutsch (German)'),
	('fa', 'Farsi (Persian)'),
	('fr', 'Francais (French)'),
	('it', 'Italian'),
	('nl', 'Dutch (Netherlands)'),
	('pt', 'Portuguese'),
	('ro', 'Romanian'),
)


# OCR dictionaries
OCR_LANGUAGES_CHOICES = (
	('eng', 'English'),
	('ara', 'Arabic'),
	('ces', 'Czech'),
	('deu', 'Deutsch (German)'),
	('deu-frak', 'Deutsch Frakturschrift (Old German)'),
	('far', 'Farsi (Persian)'),
	('hun', 'Hungarian'),
	('fra', 'Francais (French)'),
	('ita', 'Italian'),
	('nld', 'Dutch (Netherlands)'),
	('por', 'Portuguese'),
	('ron', 'Romanian'),
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
# Write setup from database to Open Semantic ETL config file
#
def	generate_etl_configfile(filename="/etc/opensemanticsearch/etl-webadmin"):

	setup = Setup.objects.get(pk=1)

	configfile = open(filename, "w", encoding="utf-8")

	configfile.write( "# Warning: Do not edit here, will be overwritten by the web admin user interface\n" )

	configfile.write( "config['languages'] = " + str(setup.languages.split(',')) + "\n" )

	configfile.write( "config['languages_force'] = " + str(setup.languages_force.split(',')) + "\n" )

	configfile.write( "config['ocr_lang'] = \'" + "+".join(setup.ocr_languages.split(',')) + "\'\n" )

	if setup.ocr:
		configfile.write( "config['ocr'] = True\n" )
	else:
		configfile.write( "config['ocr'] = False\n" )
		
	if setup.ocr_pdf:
		configfile.write( "if not 'enhance_pdf_ocr' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_pdf_ocr')" + "\n" )
	else:
		configfile.write( "if 'enhance_pdf_ocr' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_pdf_ocr')" + "\n" )
	
	if setup.ocr_descew:
		configfile.write( "if not 'enhance_ocr_descew' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_ocr_descew')" + "\n" )
	else:
		configfile.write( "if 'enhance_ocr_descew' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_ocr_descew')" + "\n" )

	if setup.ner_spacy:
		configfile.write( "if not 'enhance_ner_spacy' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_ner_spacy')" + "\n" )
	else:
		configfile.write( "if 'enhance_ner_spacy' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_ner_spacy')" + "\n" )

	if setup.ner_stanford:
		configfile.write( "if not 'enhance_ner_stanford' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_ner_stanford')" + "\n" )
	else:
		configfile.write( "if 'enhance_ner_stanford' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_ner_stanford')" + "\n" )

	configfile.close()


#
# Write setup from database to Solr PHP UI config file
#
def	generate_ui_configfile(filename="/etc/solr-php-ui/config.webadmin.php"):

	setup = Setup.objects.get(pk=1)

	configfile = open(filename, "w", encoding="utf-8")

	configfile.write( "<?php\n" )
	configfile.write( "// Warning: Do not edit here, will be overwritten by the web admin user interface\n" )


	if setup.language:	
		configfile.write( "$cfg['language'] = \'" + str(setup.language) + "\';\n" )
		
	configfile.write( "$cfg['languages'] = array(" + str(setup.languages.split(','))[1:-1] + ");\n" )

	configfile.write( "?>" )

	configfile.close()


def generate_configfiles():

	generate_etl_configfile()
	generate_ui_configfile()


#
# Updated an setup
#

def update_setup(request, pk=1):

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

			generate_configfiles()

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

