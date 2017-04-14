from django.contrib import admin
from files.models import Files


class Files_Admin(admin.ModelAdmin):
	list_display = ('title', 'uri', 'last_imported')






admin.site.register(Files, Files_Admin)
