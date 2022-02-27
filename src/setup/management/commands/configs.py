from django.core.management.base import BaseCommand, CommandError
import setup.views

class Command(BaseCommand):
    help = 'Write config files of Open Semantic ETL and Solr PHP UI from the settings in web admin UI'

    def handle(self, *args, **options):

        setup.views.generate_configfiles()

        self.stdout.write('Config files written')
