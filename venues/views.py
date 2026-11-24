from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.utils import timezone


from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import CreateView, DetailView, ListView

from .forms import VenueForm
from .models import Venue, AvailableDate, Booking, Venue
FEED_PAGE_SIZE = 5

class VenueListView(ListView):
    model = Venue
    template_name = "venues/venue_list.html"
    context_object_name = "venues"

class VenueDetailView(DetailView):
    model = Venue
    template_name = "venues/venue_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        venue = self.object
        today = timezone.localdate()
        booked = set(venue.bookings.values_list("date", flat=True))
        open_dates = venue.available_dates.filter(date__gte=today).exclude(
            date__in=booked
        )
        context["bookable_dates"] = [
            d.isoformat() for d in open_dates.values_list("date", flat=True)
        ]
        context["is_owner"] = venue.owner == self.request.user
        if context["is_owner"]:
            context["upcoming_bookings"] = venue.bookings.filter(
                date__gte=today
            ).select_related("booker")
        return context

class VenueCreateView(LoginRequiredMixin, CreateView):
    model = Venue
    form_class = VenueForm
    template_name = "venues/venue_form.html"
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

def venue_feed(request):
    return render(request, "venues/venue_feed.html")


def venue_feed_items(request):
    paginator = Paginator(Venue.objects.all(), FEED_PAGE_SIZE)
    if paginator.count == 0:
        return HttpResponse("")

    try:
        n = int(request.GET.get("page", 1))
    except ValueError:
        n = 1

    # wraps around so the feed loops forever theoretically
    page = paginator.page((n - 1) % paginator.num_pages + 1)
    return render(request, "venues/_venue_cards.html", {"venues": page.object_list})





def parse_dates(raw):
    """Turn '2026-12-01, 2026-12-05' into a set of date objects, skipping junk."""
    dates = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            dates.add(date.fromisoformat(part))
        except ValueError:
            continue
    return dates


@login_required
def manage_availability(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    if venue.owner != request.user:
        return HttpResponseForbidden("Only the venue owner can edit availability.")

    today = timezone.localdate()
    booked = set(venue.bookings.values_list("date", flat=True))

    if request.method == "POST":
        chosen = {d for d in parse_dates(request.POST.get("dates", "")) if d >= today}
        chosen |= booked  # booked dates can never be taken away
        venue.available_dates.exclude(date__in=chosen).delete()
        existing = set(venue.available_dates.values_list("date", flat=True))
        AvailableDate.objects.bulk_create(
            [AvailableDate(venue=venue, date=d) for d in chosen - existing]
        )
        messages.success(request, "Availability updated.")
        return redirect(venue)

    selected = [
        d.isoformat()
        for d in venue.available_dates.filter(date__gte=today).values_list(
            "date", flat=True
        )
    ]
    return render(
        request,
        "venues/venue_availability.html",
        {"venue": venue, "selected": selected, "booked": sorted(booked)},
    )


@login_required
def book_venue(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    if request.method != "POST":
        return redirect(venue)

    if venue.owner == request.user:
        messages.error(request, "You can't book your own venue.")
        return redirect(venue)

    event_name = request.POST.get("event_name", "").strip()
    chosen = parse_dates(request.POST.get("dates", ""))
    if not event_name or not chosen:
        messages.error(request, "Enter an event name and pick at least one date.")
        return redirect(venue)

    open_dates = set(
        venue.available_dates.filter(date__gte=timezone.localdate()).values_list(
            "date", flat=True
        )
    ) - set(venue.bookings.values_list("date", flat=True))
    if not chosen <= open_dates:
        messages.error(request, "One of those dates isn't available. Please pick again.")
        return redirect(venue)

    try:
        with transaction.atomic():
            Booking.objects.bulk_create(
                [
                    Booking(venue=venue, booker=request.user, date=d, event_name=event_name)
                    for d in sorted(chosen)
                ]
            )
    except IntegrityError:
        messages.error(
            request, "Someone just booked one of those dates. Please pick again."
        )
        return redirect(venue)

    messages.success(request, f"Booked {len(chosen)} date(s) for {event_name}.")
    return redirect(venue)