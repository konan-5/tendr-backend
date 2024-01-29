from django.db import models

from tendr_backend.common.models import Common


class CftFile(Common):
    addendum_id = models.CharField(null=True, blank=True, max_length=2048)
    title = models.CharField(null=True, blank=True, max_length=2048)
    file = models.CharField(null=True, blank=True, unique=True, max_length=2048)
    description = models.CharField(null=True, blank=True, max_length=2048)
    lang = models.CharField(null=True, blank=True, max_length=2048)
    doument_version = models.CharField(null=True, blank=True, max_length=2048)
    action = models.CharField(null=True, blank=True, max_length=2048)

    def __str__(self):
        return f"{self.title}"


class Tender(Common):
    title = models.CharField(null=True, blank=True, max_length=2048)
    resource_id = models.CharField(max_length=2048, unique=True)
    ca = models.CharField(null=True, blank=True, max_length=2048)
    info = models.TextField(null=True, blank=True)
    date_published = models.DateTimeField(null=True, blank=True)
    tenders_submission_deadline = models.CharField(null=True, blank=True, max_length=2048)
    procedure = models.CharField(null=True, blank=True, max_length=2048)
    status = models.CharField(null=True, blank=True, max_length=2048)
    notice_pdf = models.CharField(null=True, blank=True, max_length=2048)
    award_date = models.CharField(null=True, blank=True, max_length=2048)
    estimated_value = models.FloatField(null=True, blank=True, default=None)
    cycle = models.CharField(null=True, blank=True, max_length=2048)
    tender_detail = models.JSONField(default=dict, null=True, blank=True)
    cft_files = models.ManyToManyField(CftFile)
    cpv_code = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"  # noqa


class ClientInfo(Common):
    tendr_id = models.ForeignKey(Tender, on_delete=models.DO_NOTHING, null=True, blank=True, default=None)
    organisation_name = models.CharField(null=True, blank=True, max_length=2048)
    ca_abbreviation = models.CharField(null=True, blank=True, max_length=2048)
    ca_type = models.CharField(null=True, blank=True, max_length=2048)
    annex = models.CharField(null=True, blank=True, max_length=2048)
    address = models.CharField(null=True, blank=True, max_length=2048)
    eircode_or_postal_code = models.CharField(null=True, blank=True, max_length=2048)
    city = models.CharField(null=True, blank=True, max_length=2048)
    county = models.CharField(null=True, blank=True, max_length=2048)
    email = models.CharField(null=True, blank=True, max_length=2048)
    phone_number = models.CharField(null=True, blank=True, max_length=2048)
    fax = models.CharField(null=True, blank=True, max_length=2048)
    website = models.CharField(null=True, blank=True, max_length=2048)

    def __str__(self):
        return f"{self.organisation_name}"
