from django.urls import path

from .views import (
    VenueCreateView,
    VenueDetailView,
    VenueListView,
    venue_feed,
    venue_feed_items,
)

urlpatterns = [
    path("", VenueListView.as_view(), name="venue_list"),
    path("feed/", venue_feed, name="venue_feed"),
    path("feed/items/", venue_feed_items, name="venue_feed_items"),
    path("new/", VenueCreateView.as_view(), name="venue_create"),
    path("<int:pk>/", VenueDetailView.as_view(), name="venue_detail"),
]