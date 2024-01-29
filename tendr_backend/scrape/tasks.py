import time

from celery import shared_task

from config import celery_app
from tendr_backend.scrape.engine.tender import get_resource_id, main
from tendr_backend.scrape.models import Tender

# User = get_user_model()


@shared_task(time_limit=6000)
@celery_app.task()
def scrape_tender():
    """A pointless Celery task to demonstrate usage."""
    print("Start scrape task")

    # main(1)
    # time.sleep(2)
    resource_ids, total_page_number = get_resource_id()
    print(len(resource_ids), total_page_number)
    all_tenders = Tender.objects.all()
    for tender in all_tenders:
        if not resource_ids.count(tender.resource_id):
            tender.is_active = False
            tender.save()
    time.sleep(10)
    for i in range(1, total_page_number + 1):
        main(i)

    print("End scrape task")
