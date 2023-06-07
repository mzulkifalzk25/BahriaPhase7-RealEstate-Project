from django.db import models
from django.urls import reverse
from accounts.models import User
from realtors.models import Realtor


class Listing(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=15)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    area_in_marla = models.IntegerField()
    photo_main = models.ImageField(upload_to='home/')
    photo_1 = models.ImageField(upload_to='home/', blank=True)
    photo_2 = models.ImageField(upload_to='home/', blank=True)
    photo_3 = models.ImageField(upload_to='home/', blank=True)
    nearMasjid = models.BooleanField(default=True)
    nearMarket = models.BooleanField(default=True)
    list_date = models.DateTimeField(auto_now_add=True)
    realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING)

    def get_absolute_url(self):
        return reverse('listings:listing', args=(str(self.id),))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'listings'

