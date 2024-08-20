from django.db import models

class TransitData(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.CharField(max_length=100)
