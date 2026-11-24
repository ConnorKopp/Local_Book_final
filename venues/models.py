from django.db import models
from django.conf import settings
from django.urls import reverse


class Venue(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="venues"
    )
    name = models.CharField(max_length=120)
    description = models.TextField()
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    price_per_hour = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Leave blank if the space is free to use.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    

    def get_absolute_url(self):
        return reverse("venue_detail", args=[self.pk])

class AvailableDate(models.Model):
    venue = models.ForeignKey(
        Venue, on_delete=models.CASCADE, related_name="available_dates"
    )
    date = models.DateField()



    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["venue", "date"], name="unique_available_date")
        ]

    def __str__(self):
        return f"{self.venue.name} on {self.date}"


class Booking(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="bookings")
    booker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )

    
    date = models.DateField()
    event_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(
                fields=["venue", "date"], name="one_booking_per_venue_per_day"
            )
        ]

    def __str__(self):
        return f"{self.event_name} at {self.venue.name} on {self.date}"
    
