from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Owner of this department entry"
    )
    department = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.department


class Policy(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='policies'
    )
    title = models.CharField(max_length=255)
    document = models.FileField(
        upload_to='policies/',
        help_text="Upload your policy document (PDF, DOCX, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.department.department})"
