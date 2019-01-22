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

from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.dispatch import receiver
from import_export.signals import post_import

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

class FacetResource(resources.ModelResource):
	class Meta:
		model = Facet


class FacetAdmin(ImportExportModelAdmin):

	resource_class = FacetResource

	list_display = ('facet', 'label',)

	ordering = ( 'facet_order',)

	def save_model(self, request, obj, form, change):

		super(FacetAdmin, self).save_model(request, obj, form, change)

		# generate facet config for Solr-PHP-UI
		ontologies.views.write_facet_config()


@receiver(post_import, dispatch_uid='post_import')
def _post_import(model, **kwargs):
    # model is the actual model instance which after import
	# generate facet config for Solr-PHP-UI
	ontologies.views.write_facet_config()


class GroupAdmin(admin.ModelAdmin):
	list_display = ('prefLabel', 'tags')
	inlines = [ GroupTagInline, ]

	
	
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Alternate)
admin.site.register(Group, GroupAdmin)
admin.site.register(Facet, FacetAdmin)
