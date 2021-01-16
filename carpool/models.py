from django.urls import reverse, reverse_lazy
from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField
import datetime
# Create your models here.

class Place(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    #description field가 필요할까?
    address = models.CharField(max_length=200, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('carpool_sel', args=[self.id])


class Pool(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='pool')
    load = models.PositiveIntegerField(null=False)
    number = models.PositiveSmallIntegerField(null=False)
    departure_date = models.DateTimeField(null=True) #나중에 가능하면 지금 이후로만 가능하도록 하자
    gap_lat = models.FloatField(default=0)
    gap_lon = models.FloatField(default=0)
    kakao_url = models.CharField(max_length=200, null=True)
    #kakao_url 은 생각을 해봐야 할 듯... 자동으로 만들어주는 것인지?
    created = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        return reverse('join', args=[self.id])
        #return reverse('carpool', args=[])


class Profile(models.Model):
    user = AutoOneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    pool = models.ForeignKey(Pool, on_delete=models.SET_NULL, null=True, blank=True)
    load = models.PositiveIntegerField(null=True, default=None, blank=True)
    number = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    status = models.PositiveSmallIntegerField(default=0)

