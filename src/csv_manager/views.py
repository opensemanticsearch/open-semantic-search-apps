from django.shortcuts import render
from django.core.urlresolvers import reverse

from csv_manager.models import CSV_Manager
from django.http import HttpResponse 

from django.views import generic

from opensemanticetl.enhance_csv import enhance_csv

import os.path


class IndexView(generic.ListView):
	model = CSV_Manager

class DetailView(generic.DetailView):
	model = CSV_Manager

class CreateView(generic.CreateView):
	model = CSV_Manager
	fields = '__all__'

class UpdateView(generic.UpdateView):
	model = CSV_Manager
	fields = '__all__'


def preview_csv(request, pk):
	table = False

	return render(request, 'csv_manager/csv_manager_preview.html', {'id': pk, 'table': table,})


def index_csv(request, pk):

	# todo:
	# - background thread writing status in db?
	#   after starting thread redirect to reloading (until ready) jobstatus page or ajax part inside status page
	# - collect exceptions for error log / status message

	verbose = True
	
	csvmanager = CSV_Manager.objects.get(pk=pk)
	
	#
	# Read parameters from form and set parameters for the csv data enrichment
	#

	if csvmanager.file:
		csvfilename = csvmanager.file.path
		id = csvmanager.file.name
		
	else:
		csvfilename = csvmanager.uri
		id = csvmanager.uri
	
	
	if csvmanager.delimiter_is_tab:
		delimiter = "\t"
	else:
		delimiter = csvmanager.delimiter

		
	data = {}
		
	parameters={}

	parameters['id']= id

	parameters['verbose'] = verbose

	parameters['filename'] = csvfilename

	parameters['delimiter'] = delimiter
	
	if csvmanager.codec:
		parameters['encoding'] = csvmanager.codec
	if csvmanager.quotechar:
		parameters['quotechar'] = csvmanager.quotechar

	parameters['doublequote'] = csvmanager.doublequote
	
	parameters['escapechar'] = csvmanager.escapechar
	
	parameters['sniff_dialect'] = csvmanager.sniff_dialect
	
	parameters['sniff_encoding'] = csvmanager.sniff_encoding
	
	parameters['title_row'] = csvmanager.title_row
	
	parameters['start_row'] = csvmanager.start_row

	parameters['cols'] = csvmanager.cols
	parameters['rows'] = csvmanager.rows
	parameters['cols_include'] = csvmanager.cols_include
	parameters['rows_include'] = csvmanager.rows_include




	# extract a list of row numbers as integer from new line and comma seperated list (textfield)
	rows = []

	for row in csvmanager.rows:
		
		for number in row.split(","):
			try:
				rows.append( int(number) )
			except:
				print ("Error converting string value to included line number: {}".format(number))
	
	parameters['rows'] = rows

	parameters['rows_include'] = csvmanager.rows_include


	# extract a list of column numbers as integer from new line and comma seperated list (textfield)
	cols = []

	for col in csvmanager.cols:
		
		for number in col.split(","):
			try:
				cols.append( int(number) )
			except:
				print ("Error converting string value to included line number: {}".format(number))
	
	parameters['cols'] = cols

	parameters['cols_include'] = csvmanager.cols_include



	#
	# Start data enrichment plugin
	#
	
	etl = enhance_csv()

	count = etl.enhance_csv ( parameters=parameters, data=data )


	return render(request, 'csv_manager/csv_manager_import.html', {'id': pk, 'count': count,})
