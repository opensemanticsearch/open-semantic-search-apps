from django.contrib import admin
from rss_manager.models import RSS_Feed


class RSS_Feed_Admin(admin.ModelAdmin):
	list_display = ('title', 'uri', 'last_imported')






admin.site.register(RSS_Feed, RSS_Feed_Admin)
