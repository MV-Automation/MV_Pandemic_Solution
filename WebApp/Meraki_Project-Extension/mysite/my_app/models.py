from django.db import models

# Create your models here.
class Doctor(models.Model):
    name=models.CharField(max_length=50)
    surname=models.CharField(max_length=50)
    date=models.TextField()
    time=models.TextField()
    motive=models.TextField()
