import time

from django.core.management.base import BaseCommand

from tendr_backend.scrape.engine.tender import get_resource_id, main
from tendr_backend.scrape.models import Tender


class Command(BaseCommand):
    help = "My shiny new management command."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        print("Start scrape task")
        for i in range(48):
            main(i)
        # time.sleep(2)
        # resource_ids, total_page_number = get_resource_id()
        # print(len(resource_ids), total_page_number)
        # all_tenders = Tender.objects.all()
        # for tender in all_tenders:
        #     if not resource_ids.count(tender.resource_id):
        #         tender.is_active = False
        #         tender.save()

        print("End scrape task")
