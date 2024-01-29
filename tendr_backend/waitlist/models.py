from django.contrib.auth import get_user_model
from django.db import models

from tendr_backend.common.models import Common
from tendr_backend.common.utils.helper import send_email_smtp
from tendr_backend.scrape.models import Tender

User = get_user_model()


class Waiter(Common):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    company = models.CharField(max_length=255)
    phone = models.CharField(max_length=16, blank=True, null=True)
    other = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # Your custom action before saving
        # Example: print a message
        print(f"Saving waiter: {self.full_name}")

        # Call the real save() method
        super().save(*args, **kwargs)

        email_content = (
            f"Full Name: {self.full_name}\n"
            f"Email: {self.email}\n"
            f"Company: {self.company}\n"
            f"Phone: {self.phone if self.phone else 'Not provided'}\n"
            f"Other Info: {self.other if self.other else 'Not provided'}"
        )
        send_email_smtp("New Waiter", email_content, "daniel.tendr@gmail.com")


class WaitDocument(Common):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tendr_id = models.ForeignKey(Tender, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("user_id", "tendr_id"),)
