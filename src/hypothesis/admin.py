from django.contrib import admin
from hypothesis.models import Hypothesis


class Hypothesis_Admin(admin.ModelAdmin):
	list_display = ('title', 'user','group','tag','uri', 'last_imported')

admin.site.register(Hypothesis, Hypothesis_Admin)
