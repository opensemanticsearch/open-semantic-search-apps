from django.contrib import admin
from django.contrib import messages
from thesaurus.models import Concept
from thesaurus.models import ConceptTag
from thesaurus.models import Alternate
from thesaurus.models import Group
from thesaurus.models import GroupTag
from thesaurus.models import Facet
import thesaurus.views
import ontologies.views


class AlternateInline(admin.TabularInline):
    model = Alternate
    extra = 0


class GroupTagInline(admin.TabularInline):
	model = GroupTag
	extra = 0


class ConceptTagInline(admin.TabularInline):
	model = ConceptTag
	extra = 0


class ConceptAdmin(admin.ModelAdmin):
	list_display = ('prefLabel', 'alternates',)
	inlines = [ ConceptTagInline, AlternateInline, ]
	filter_horizontal = ('groups',)


	def save_model(self, request, obj, form, change):

		super(ConceptAdmin, self).save_model(request, obj, form, change)

		# tag all docs containing concept or one of its aliases
		thesaurus.views.tag_concept_and_message_stats(request=request, concept=obj)


class FacetAdmin(admin.ModelAdmin):
	list_display = ('facet', 'label',)

	def save_model(self, request, obj, form, change):

		super(FacetAdmin, self).save_model(request, obj, form, change)

		# generate facet config for Solr-PHP-UI
		ontologies.views.write_facet_config()


class GroupAdmin(admin.ModelAdmin):
	list_display = ('prefLabel', 'tags')
	inlines = [ GroupTagInline, ]

	
	
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Alternate)
admin.site.register(Group, GroupAdmin)
admin.site.register(Facet, FacetAdmin)
