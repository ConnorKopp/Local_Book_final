from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView

from .forms import VenueForm
from .models import Venue
FEED_PAGE_SIZE = 5

class VenueListView(ListView):
    model = Venue
    template_name = "venues/venue_list.html"
    context_object_name = "venues"

class VenueDetailView(DetailView):
    model = Venue
    template_name = "venues/venue_detail.html"

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