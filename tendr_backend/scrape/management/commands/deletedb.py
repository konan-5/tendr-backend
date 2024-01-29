from django.conf import settings
from django.core.management.base import BaseCommand

from tendr_backend.scrape.engine.aws_s3 import delete_from_s3
from tendr_backend.scrape.engine.local import delete_all_files_in_directory
from tendr_backend.scrape.models import CftFile, ClientInfo, Tender


class Command(BaseCommand):
    help = "My shiny new management command."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        pass
        # cft_files = CftFile.objects.all()
        # for obj in cft_files:
        #     if obj.file is not None:
        #         obj.file.replace("https://tendr.s3.eu-west-1.amazonaws.com/", "")
        #         delete_from_s3(obj.file)
        # cft_files.delete()

        # ClientInfo.objects.all().delete()

        # tenders = Tender.objects.all()
        # for obj in tenders:
        #     if obj.notice_pdf is not None:
        #         obj.notice_pdf.replace("https://tendr.s3.eu-west-1.amazonaws.com/", "")
        #         delete_from_s3(obj.notice_pdf)
        # tenders.delete()
        # delete_all_files_in_directory(f"{settings.MEDIA_ROOT}/cft-files")
        # delete_all_files_in_directory(f"{settings.MEDIA_ROOT}/notice-pdfs")
