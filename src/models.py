from django.db import models


# Create your models here.


class Audio(models.Model):
    document = models.FileField(null=True)
    audio = models.FileField()
