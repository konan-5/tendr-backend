from django.contrib import admin

from .models import CftFile, ClientInfo, Tender


@admin.register(CftFile)
class CftFileAdmin(admin.ModelAdmin):
    list_display = (
        "addendum_id",
        "title",
        "file",
        "description",
        "lang",
        "doument_version",
        "action",
    )
    search_fields = ("title",)


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "resource_id",
        "ca",
        # "info",
        "date_published",
        "tenders_submission_deadline",
        "procedure",
        "status",
        "notice_pdf",
        "award_date",
        "estimated_value",
        "cycle",
        # "tender_detail",
        "cft_files_list",
        "created_at",
    )
    search_fields = ("title", "resource_id", "date_published")

    @admin.display(description="Cft Files")
    def cft_files_list(self, obj):
        # return "\n".join([f"{cft_file.title[:9]}...-{str(cft_file.file)}" for cft_file in obj.cft_files.all()])
        return "\n".join([f"{cft_file.file}" for cft_file in obj.cft_files.all()])


@admin.register(ClientInfo)
class ClientInfoAdmin(admin.ModelAdmin):
    list_display = (
        "organisation_name",
        "ca_abbreviation",
        "ca_type",
        "annex",
        "address",
        "eircode_or_postal_code",
        "city",
        "county",
        "email",
        "phone_number",
        "fax",
        "website",
    )
    search_fields = ("organisation_name",)
