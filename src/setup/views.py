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
	('ru', 'Russian'),
)

LANGUAGES_CHOICES_HUNSPELL = (
	('hu', 'Hungarian'),
)


# OCR dictionaries
OCR_LANGUAGES_CHOICES = (
	('Arabic', 'data for Arabic script'),
	('Armenian', 'data for Armenian script'),
	('Bengali', 'data for Bengali script'),
	('Canadian_Aboriginal', 'data for Canadian Aboriginal script'),
	('Cherokee', 'data for Cherokee script'),
	('Cyrillic', 'data for Cyrillic script'),
	('Devanagari', 'data for Devanagari script'),
	('Ethiopic', 'data for Ethiopic script'),
	('Fraktur', 'data for Fraktur script'),
	('Georgian', 'data for Georgian script'),
	('Greek', 'data for Greek script'),
	('Gujarati', 'data for Gujarati script'),
	('Gurmukhi', 'data for Gurmukhi script'),
	('Hangul', 'data for Hangul script'),
	('Hangul_vert', 'data for Hangul (vertical) script'),
	('HanS', 'data for Han - Simplified script'),
	('HanS_vert', 'data for Han - Simplified (vertical) script'),
	('HanT', 'data for Han - Traditional script'),
	('HanT_vert', 'data for Han - Traditional (vertical) script'),
	('Hebrew', 'data for Hebrew script'),
	('Japanese', 'data for Japanese script'),
	('Japanese_vert', 'data for Japanese (vertical) script'),
	('Khmer', 'data for Khmer script'),
	('Kannada', 'data for Kannada script'),
	('Lao', 'data for Lao script'),
	('Latin', 'data for Latin script'),
	('Malayalam', 'data for Malayalam script'),
	('Myanmar', 'data for Myanmar script'),
	('Oriya', 'data for Oriya (Odia) script'),
	('Sinhala', 'data for Sinhala script'),
	('Syriac', 'data for Syriac script'),
	('Tamil', 'data for Tamil script'),
	('Telugu', 'data for Telugu script'),
	('Thaana', 'data for Thaana script'),
	('Thai', 'data for Thai script'),
	('Tibetan', 'data for Tibetan script'),
	('Vietnamese', 'data for Vietnamese script'),
	('afr', 'Afrikaans'),
	('amh', 'Amharic'),
	('ara', 'Arabic'),
	('asm', 'Assamese'),
	('aze', 'Azerbaijani'),
	('aze_cyrl', 'Azerbaijani (Cyrillic)'),
	('bel', 'Belarusian'),
	('ben', 'Bengali'),
	('bod', 'Tibetan Standard'),
	('bos', 'Bosnian'),
	('bul', 'Bulgarian'),
	('cat', 'Catalan'),
	('ceb', 'Cebuano'),
	('ces', 'Czech'),
	('chi_sim', 'Chinese  - Simplified'),
	('chi_sim_vert', 'Chinese - Simplified (vertical)'),
	('chi_tra', 'Chinese - Traditional'),
	('chi_tra_vert', 'Chinese - Traditional (vertical)'),
	('chr', 'Cherokee'),
	('cos', 'Corsican'),
	('cym', 'Welsh'),
	('dan', 'Danish'),
	('deu', 'German'),
	('div', 'Divehi'),
	('dzo', 'Dzongkha'),
	('ell', 'Greek'),
	('eng', 'English'),
	('enm', 'English, Middle (1100-1500)'),
	('epo', 'Esperanto'),
	('est', 'Estonian'),
	('eus', 'Basque'),
	('fao', 'Faroese'),
	('fas', 'Persian'),
	('fil', 'Filipino'),
	('fin', 'Finnish'),
	('fra', 'French'),
	('frk', 'German (Fraktur)'),
	('frm', 'French, Middle (ca.1400-1600)'),
	('fry', 'Frisian (Western)'),
	('gla', 'Gaelic (Scots)'),
	('gle', 'Irish'),
	('glg', 'Galician'),
	('guj', 'Gujarati'),
	('hat', 'Hatian'),
	('heb', 'Hebrew'),
	('hin', 'Hindi'),
	('hrv', 'Croatian'),
	('hun', 'Hungarian'),
	('hye', 'Armenian'),
	('iku', 'Inuktitut'),
	('ind', 'Indonesian'),
	('isl', 'Icelandic'),
	('ita', 'Italian'),
	('ita_old', 'Italian - Old'),
	('jav', 'Javanese'),
	('jpn', 'Japanese'),
	('jpn_vert', 'Japanese (vertical)'),
	('kan', 'Kannada'),
	('kat', 'Georgian'),
	('kat_old', 'Old Georgian'),
	('kaz', 'Kazakh'),
	('khm', 'Khmer'),
	('kir', 'Kyrgyz'),
	('kor', 'Korean'),
	('kor_vert', 'Korean (vertical)'),
	('kur_ara', 'Kurdish (Arabic)'),
	('lao', 'Lao'),
	('lat', 'Latin'),
	('lav', 'Latvian'),
	('lit', 'Lithuanian'),
	('ltz', 'Luxembourgish'),
	('mal', 'Malayalam'),
	('mar', 'Marathi'),
	('mkd', 'Macedonian'),
	('mlt', 'Maltese'),
	('mon', 'Mongolian'),
	('mri', 'Maori'),
	('msa', 'Malay'),
	('mya', 'Burmese'),
	('nep', 'Nepali'),
	('nld', 'Dutch'),
	('nor', 'Norwegian'),
	('oci', 'Occitan (post 1500)'),
	('ori', 'Oriya'),
	('osd', 'script and orientation'),
	('pan', 'Punjabi'),
	('pol', 'Polish'),
	('por', 'Portuguese'),
	('pus', 'Pashto'),
	('que', 'Quechua'),
	('ron', 'Romanian'),
	('rus', 'Russian'),
	('san', 'Sanskrit'),
	('sin', 'Sinhala'),
	('slk', 'Slovak'),
	('slv', 'Slovenian'),
	('snd', 'Sindhi'),
	('spa', 'Spanish'),
	('spa_old', 'Spanish, Castilian - Old'),
	('sqi', 'Albanian'),
	('srp', 'Serbian'),
	('srp_latn', 'Serbian (Latin)'),
	('sun', 'Sudanese'),
	('swa', 'Swahili'),
	('swe', 'Swedish'),
	('syr', 'Syriac'),
	('tam', 'Tamil'),
	('tat', 'Tatar'),
	('tel', 'Telugu'),
	('tgk', 'Tajik'),
	('tha', 'Thai'),
	('tir', 'Tigrinya'),
	('ton', 'Tonga'),
	('tur', 'Turkish'),
	('uig', 'Uyghur'),
	('ukr', 'Ukranian'),
	('urd', 'Urdu'),
	('uzb', 'Uzbek'),
	('uzb_cyrl', 'Uzbek (Cyrillic)'),
	('vie', 'Vietnamese'),
	('yid', 'Yiddish'),
	('yor', 'Yoruba'),
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

	if setup.ocr_later and (setup.ocr or setup.ocr_pdf):
		# initialize (yet empty) config options for running plugins later, which will be set/appended there in further steps
		configfile.write( "if not 'additional_plugins_later' in config:\n" )
		configfile.write( "\tconfig['additional_plugins_later'] = []" + "\n" )
		configfile.write( "if not 'additional_plugins_later_config' in config:\n" )
		configfile.write( "\tconfig['additional_plugins_later_config'] = {}" + "\n" )
		

	if setup.ocr:

		if setup.ocr_later:
			configfile.write( "config['ocr'] = False\n" )
			configfile.write( "config['additional_plugins_later_config']['ocr'] = True\n" )
		else:
			configfile.write( "config['ocr'] = True\n" )
			
	else:
		configfile.write( "config['ocr'] = False\n" )
		
	if setup.ocr_pdf:

		if setup.ocr_later:
			configfile.write( "if 'enhance_pdf_ocr' in config['plugins']:" + "\n" )
			configfile.write( "\tconfig['plugins'].remove('enhance_pdf_ocr')" + "\n" )
			configfile.write( "if not 'enhance_pdf_ocr' in config['additional_plugins_later']:" + "\n" )
			configfile.write( "\tconfig['additional_plugins_later'].append('enhance_pdf_ocr')" + "\n" )
			
		else:
			configfile.write( "if not 'enhance_pdf_ocr' in config['plugins']:" + "\n" )
			configfile.write( "\tconfig['plugins'].append('enhance_pdf_ocr')" + "\n" )

	else:
		configfile.write( "if 'enhance_pdf_ocr' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_pdf_ocr')" + "\n" )
	
	if setup.ocr_descew:

		if setup.ocr_later:
			configfile.write( "if 'enhance_ocr_descew' in config['plugins']:" + "\n" )
			configfile.write( "\tconfig['plugins'].remove('enhance_ocr_descew')" + "\n" )
			configfile.write( "if not 'enhance_ocr_descew' in config['additional_plugins_later']:" + "\n" )
			configfile.write( "\tconfig['additional_plugins_later'].append('enhance_ocr_descew')" + "\n" )
		else:
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

	if setup.segmentation_sentences:
		configfile.write( "if not 'enhance_sentence_segmentation' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].append('enhance_sentence_segmentation')" + "\n" )
	else:
		configfile.write( "if 'enhance_sentence_segmentation' in config['plugins']:" + "\n" )
		configfile.write( "\tconfig['plugins'].remove('enhance_sentence_segmentation')" + "\n" )

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
