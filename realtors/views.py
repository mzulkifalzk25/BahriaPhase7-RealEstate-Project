from django.shortcuts import render, get_object_or_404
from .models import Realtor


def realtors(request):
    realtors = Realtor.objects.all()
    context = {
        'realtors': realtors
    }
    return render(request, 'realtors/all-realtors.html', context)


def realtor(request, realtor_id):
    realtor = get_object_or_404(Realtor, pk=realtor_id)
    listings = realtor.listing_set.order_by('-list_date')
    context = {
        'realtor': realtor,
        'listings': listings
    }
    return render(request, 'realtors/agent-single.html', context)



