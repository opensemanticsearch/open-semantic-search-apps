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
from ontologies.models import Ontologies


# Language of UI
LANGUAGE_CHOICES = (
	('en', 'English'),
	('ar', 'Arabic'),
	('de', 'Deutsch (German)'),
	('it', 'Italian'),
	('pt', 'Portuguese'),
	('fr', 'French (Switzerland)')
)


# Grammar / Stemming languages
LANGUAGES_CHOICES = (
	('en', 'English'),
	('ar', 'Arabic'),
	('cz', 'Czech'),
	('de', 'Deutsch (German)'),
	('fa', 'Farsi (Persian)'),
	('fr', 'Francais (French)'),
	('hu', 'Hungarian'),
	('it', 'Italian'),
	('nl', 'Dutch (Netherlands)'),
	('pt', 'Portuguese'),
	('ro', 'Romanian'),
)

LANGUAGES_CHOICES_HUNSPELL = (
	('hu', 'Hungarian'),
)


# OCR dictionaries
OCR_LANGUAGES_CHOICES = (
	('afr', 'Afrikaans'),
	('amh', 'Amharic'),
	('ara', 'Arabic'),
	('asm', 'Assamese'),
	('aze', 'Azerbaijani'),
	('aze-cyrl', 'Azerbaijani (Cyrillic)'),
	('bel', 'Belarusian'),
	('ben', 'Bengali'),
	('bod', 'Tibetan Standard'),
	('bos', 'Bosnian'),
	('bul', 'Bulgarian'),
	('cat', 'Catalan'),
	('ceb', 'Cebuano'),
	('ces', 'Czech'),
	('chi-sim', 'Simplified Chinese'),
	('chi-tra', 'Traditional Chinese'),
	('chr', 'Cherokee'),
	('cym', 'Welsh'),
	('dan', 'Danish'),
	('dan-frak', 'Danish (Fraktur)'),
	('deu', 'German'),
	('deu-frak', 'German Fraktur'),
	('dzo', 'Dzongkha'),
	('ell', 'Greek'),
	('eng', 'English'),
	('enm', 'Middle English'),
	('epo', 'Esperanto'),
	('equ', 'equations'),
	('est', 'Estonian'),
	('eus', 'Basque'),
	('fas', 'Persian'),
	('fin', 'Finnish'),
	('fra', 'French'),
	('frk', 'Frankish'),
	('frm', 'Middle French'),
	('gle', 'Irish'),
	('gle-uncial', 'Irish (Uncial)'),
	('glg', 'Galician'),
	('grc', 'Ancient Greek'),
	('guj', 'Gujarati'),
	('hat', 'Hatian'),
	('heb', 'Hebrew'),
	('hin', 'Hindi'),
	('hrv', 'Croatian'),
	('hun', 'Hungarian'),
	('iku', 'Inuktitut'),
	('ind', 'Indonesian'),
	('isl', 'Icelandic'),
	('ita', 'Italian'),
	('ita-old', 'Old Italian'),
	('jav', 'Javanese'),
	('jpn', 'Japanese'),
	('kan', 'Kannada'),
	('kat', 'Georgian'),
	('kat-old', 'Old Georgian'),
	('kaz', 'Kazakh'),
	('khm', 'Khmer'),
	('kir', 'Kyrgyz'),
	('kor', 'Korean'),
	('kur', 'Kurdish'),
	('lao', 'Lao'),
	('lat', 'Latin'),
	('lav', 'Latvian'),
	('lit', 'Lithuanian'),
	('mal', 'Malayalam'),
	('mar', 'Marathi'),
	('mkd', 'Macedonian'),
	('mlt', 'Maltese'),
	('msa', 'Malay'),
	('mya', 'Burmese'),
	('nep', 'Nepali'),
	('nld', 'Dutch'),
	('nor', 'Norwegian'),
	('ori', 'Oriya'),
	('osd', 'script and orientation'),
	('pan', 'Punjabi'),
	('pol', 'Polish'),
	('por', 'Portuguese'),
	('pus', 'Pashto'),
	('ron', 'Romanian'),
	('rus', 'Russian'),
	('san', 'Sanskrit'),
	('sin', 'Sinhala'),
	('slk', 'Slovak'),
	('slk-frak', 'Slovak Fractur'),
	('slv', 'Slovenian'),
	('spa', 'Spanish'),
	('spa-old', 'Old Spanish'),
	('sqi', 'Albanian'),
	('srp', 'Serbian'),
	('srp-latn', 'Serbian (Latin)'),
	('swa', 'Swahili'),
	('swe', 'Swedish'),
	('syr', 'Syriac'),
	('tam', 'Tamil'),
	('tel', 'Telugu'),
	('tgk', 'Tajik'),
	('tgl', 'Tagalog'),
	('tha', 'Thai'),
	('tir', 'Tigrinya'),
	('tur', 'Turkish'),
	('uig', 'Uyghur'),
	('ukr', 'Ukranian'),
	('urd', 'Urdu'),
	('uzb', 'Uzbek'),
	('uzb-cyrl', 'Uzbek (Cyrillic)'),
	('vie', 'Vietnamese'),
	('yid', 'Yiddish'),
)


class SetupForm(ModelForm):

	class Meta:
		model = Setup
		exclude = ['language', 'languages', 'languages_force', 'languages_hunspell', 'languages_force_hunspell', 'ocr_languages']

		
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

	languages_hunspell = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES_HUNSPELL,
    )

	languages_force_hunspell = forms.MultipleChoiceField(
		required=False,
		widget=forms.CheckboxSelectMultiple,
		choices=LANGUAGES_CHOICES_HUNSPELL,
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

	if setup.languages:
		languages = setup.languages.split(',')
	else:
		languages = []

	configfile.write( "config['languages'] = " + str(languages) + "\n" )

	if setup.languages_force:
		languages_force = setup.languages_force.split(',')
	else:
		languages_force = []

	configfile.write( "config['languages_force'] = " +  str(languages_force) + "\n" )

	if setup.languages_hunspell:
		languages_hunspell = setup.languages_hunspell.split(',')
	else:
		languages_hunspell = []

	configfile.write( "config['languages_hunspell'] = " + str(languages_hunspell) + "\n" )

	if setup.languages_force_hunspell:
		languages_force_hunspell = setup.languages_force_hunspell.split(',')
	else:
		languages_force_hunspell = []

	configfile.write( "config['languages_force_hunspell'] = " +  str(languages_force_hunspell) + "\n" )

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

	if setup.segmentation_pages:
		configfile.write( "if not 'enhance_pdf_page' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_pdf_page')" + "\n" )
	else:
		configfile.write( "if 'enhance_pdf_page' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_pdf_page')" + "\n" )

	if setup.segmentation_pages_preview:
		configfile.write( "if not 'enhance_pdf_page_preview' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_pdf_page_preview')" + "\n" )
	else:
		configfile.write( "if 'enhance_pdf_page_preview' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_pdf_page_preview')" + "\n" )

	if setup.graph_neo4j:
		configfile.write( "if not 'export_neo4j' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('export_neo4j')" + "\n" )
		if setup.graph_neo4j_host:
			configfile.write( "config['neo4j_host'] = '" + str(setup.graph_neo4j_host) + "'\n" )
		if setup.graph_neo4j_user:
			configfile.write( "config['neo4j_user'] = '" + str(setup.graph_neo4j_user) + "'\n" )
		if setup.graph_neo4j_password:
			configfile.write( "config['neo4j_password'] = '" + str(setup.graph_neo4j_password) + "'\n" )
	else:
		configfile.write( "if 'export_neo4j' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('export_neo4j')" + "\n" )


	#
	# Entity extraction stemming config
	#

	entity_linking_taggers = ['all_labels_ss_tag']
	entity_linking_taggers_document_language_dependent = {}
	
	# set stemming fields / text tagger config for named entity extraction from activated stemmers of all ontologies
	for ontology in Ontologies.objects.all():

		# forced stemmers

		if ontology.stemming_force:
			for language in ontology.stemming_force.split(','):
				tagger = 'all_labels_stemming_force_' + language + '_ss_tag'
				if not tagger in entity_linking_taggers:
					entity_linking_taggers.append(tagger)

		if ontology.stemming_force_hunspell:
			for language in ontology.stemming_force_hunspell.split(','):
				tagger = 'all_labels_stemming_force_hunspell_' + language + '_ss_tag'
				if not tagger in entity_linking_taggers:
					entity_linking_taggers.append(tagger)
		
		# document language dependent stemmers
		
		if ontology.stemming:
			for language in ontology.stemming.split(','):
				if not language in entity_linking_taggers_document_language_dependent:
					entity_linking_taggers_document_language_dependent[language] = []
				tagger = 'all_labels_stemming_' + language + '_ss_tag'
				if not tagger in entity_linking_taggers_document_language_dependent[language]:
					entity_linking_taggers_document_language_dependent[language].append(tagger)

		if ontology.stemming_hunspell:
			for language in ontology.stemming_hunspell.split(','):
				if not language in entity_linking_taggers_document_language_dependent:
					entity_linking_taggers_document_language_dependent[language] = []
				tagger = 'all_labels_stemming_hunspell_' + language + '_ss_tag'
				if not tagger in entity_linking_taggers_document_language_dependent[language]:
					entity_linking_taggers_document_language_dependent[language].append(tagger)

	configfile.write( "config['entity_linking_taggers'] = " +  str(entity_linking_taggers) + "\n" )

	configfile.write( "config['entity_linking_taggers_document_language_dependent'] = " +  str(entity_linking_taggers_document_language_dependent) + "\n" )
		

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
		
	languages = []

	if setup.languages:
		for language in setup.languages.split(','):
			languages.append("'" + language + "'")

	if setup.languages_hunspell:
		for language in setup.languages_hunspell.split(','):
			languages.append("'hunspell_" + language + "'")

	configfile.write( "$cfg['languages'] = array(" + ','.join(languages)  + ");\n" )


	if setup.graph_neo4j and setup.graph_neo4j_browser:	
		configfile.write( "$cfg['neo4j_browser'] = \'" + str(setup.graph_neo4j_browser) + "\';\n" )


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
			setup.languages_hunspell = (',').join( form.cleaned_data['languages_hunspell'] )
			setup.languages_force_hunspell = (',').join( form.cleaned_data['languages_force_hunspell'] )
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
		languages_hunspell = setup.languages_hunspell.split(",")
		languages_force_hunspell = setup.languages_force_hunspell.split(",")
		ocr_languages = setup.ocr_languages.split(",")

		form = SetupForm( instance=setup, initial={ 'language': language, 'languages': languages, 'languages_force': languages_force, 'languages_hunspell': languages_hunspell, 'languages_force_hunspell': languages_force_hunspell, 'ocr_languages': ocr_languages } )

	return render(request, 'setup/setup_form.html', 
			{'form': form, 'setup': setup } )


def setup_language(request):

	setup = Setup.objects.get(pk=1)

	setup.language = request.GET["language"]

	setup.languages_force = request.GET["languagesforce"]
	
	setup.languages = request.GET["languages"]
	
	setup.ocr_languages = request.GET["ocrlanguages"]
	
	setup.save()
	
	generate_configfiles()

	return HttpResponse()
