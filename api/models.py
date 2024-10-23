from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    # Additional fields can be added here if needed
    pass

User = get_user_model()

class Place(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    category = models.CharField(max_length=100)
    average_time_spent = models.IntegerField(help_text='Average time spent in minutes')
    entry_fee = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_outdoor = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    places = models.ManyToManyField(Place, through='ItineraryPlace')
    created_at = models.DateTimeField(auto_now_add=True)
    total_time = models.IntegerField(help_text='Total time in minutes', null=True, blank=True)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Itinerary for {self.user.username} on {self.created_at.date()}"

class ItineraryPlace(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    time_allocated = models.IntegerField(help_text='Time allocated in minutes')

    class Meta:
        ordering = ['order']