from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.IntegerField()
    email = models.CharField(max_length=50)
    content = models.CharField(max_length=250)

    def __str__(self):
        return self.name
