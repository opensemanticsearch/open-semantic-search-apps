from django.core.management.base import BaseCommand, CommandError
import ontologies.views

class Command(BaseCommand):
    help = 'Setup of facets, thesaurus and ontologies for Open Semantic ETL and Open Semantic Entity Search API'

    def handle(self, *args, **options):

        ontologies.views.write_named_entities_config()

        self.stdout.write('Entities setup done')
