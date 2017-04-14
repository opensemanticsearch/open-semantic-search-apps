from django.contrib import admin
from crawler.models import Crawler


class Crawler_Admin(admin.ModelAdmin):
	list_display = ('title', 'uri', 'last_imported')






admin.site.register(Crawler, Crawler_Admin)
