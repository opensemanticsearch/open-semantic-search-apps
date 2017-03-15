from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse 

import datetime
from datetime import timedelta

from etl.tasks import index_rss

from models import RSS_Feed

#
# add feeds to queue if last import before delta time
#

def import_feeds(request):

	verbose = True

	log = []
	count = 0
	count_queued = 0

	for feed in RSS_Feed.objects.all():

		count += 1

		if verbose:
			log.append( "Checking delta time of feed: {}".format(feed) ) 

		add_to_queue = True

		# If delta time, do not import this feed in within this time
		if feed.delta and feed.last_imported:

			# when next import allowed (because time delta passed)?
			next_import = feed.last_imported + timedelta(minutes=feed.delta)

			# don't check time delta if last import in future (i.e. if system time was wrong)
			if feed.last_imported < timezone.now():			

				# if time for next import not reached, do not index
				if timezone.now() < next_import:
					add_to_queue = False

			if verbose:
				log.append( "Last import: {}".format(feed.last_imported) )
				log.append( "Next import: {}".format(next_import) ) 


		if add_to_queue:
			
			if verbose:
				log.append( "Adding feed to queue: {}".format(feed) ) 

			# add to queue
			last_imported = datetime.datetime.now()
			index_rss.delay(uri=feed.uri)

			# save new timestamp
			feed.last_imported = last_imported
			feed.save()

			count_queued += 1
	
	#
 	# stats / log
 	#
 	
	response = "Feeds to queue: {} of {}".format(count_queued, count)

	if len(log) > 0:
		response += "\n\n" + "\n".join(log)
	
	#
	# return response
	#
	
	status = HttpResponse(response)
	status["Content-Type"] = "text/plain" 
	return status
