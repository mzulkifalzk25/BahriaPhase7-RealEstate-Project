import os
import pickle
from django.conf import settings
from sklearn.ensemble import RandomForestRegressor
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.core.mail import send_mail
from realtors.models import Realtor
from .forms import ContactForm
from .models import Listing


def index(request):
    listings = Listing.objects.all()
    paginator = Paginator(listings, 3)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)
    
    realtors = Realtor.objects.all()
    realtors_paginator = Paginator(realtors, 3)
    realtors_page = request.GET.get('page')
    realtors_paged_listings = realtors_paginator.get_page(realtors_page)

    context = {
        'listings': paged_listings,
        'realtors': realtors_paged_listings,
    }

    return render(request, 'listings/index.html', context)


def listings(request):
    # listings = Listing.objects.order_by('-list_date')
    listings = Listing.objects.all()

    paginator = Paginator(listings, 3)
    page = request.GET.get('page')
    paged_listings = paginator.get_page(page)

    context = {
        'listings': paged_listings
    }

    return render(request, 'listings/houses.html', context)


def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    realtor = Realtor.objects.all()

    context = {
        'listing': listing,
        'realtor': realtor
    }

    return render(request, 'listings/house.html', context)


def search(request):
    queryset_list = Listing.objects.order_by('-list_date')

    keywords = request.GET.get('keywords')
    if keywords:
        queryset_list = queryset_list.filter(description__icontains=keywords)

    city = request.GET.get('city')
    if city:
        queryset_list = queryset_list.filter(city__iexact=city)

    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        queryset_list = queryset_list.filter(bedrooms__exact=bedrooms)

    bathrooms = request.GET.get('bathrooms')
    if bathrooms:
        queryset_list = queryset_list.filter(bathrooms__exact=bathrooms)

    price = request.GET.get('price')
    if price:
        queryset_list = queryset_list.filter(price__lte=price)

    context = {
        'listings': queryset_list,
        'values': request.GET
    }

    return render(request, 'listings/search.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            listing_id = form.cleaned_data['listing_id']
            listing = Listing.objects.get(id=listing_id)
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            message = form.cleaned_data['message']
            # Send email to agent with user's message
            subject = f'New message regarding {listing.title}'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [listing.realtor.email]
            context = {
                'listing': listing,
                'name': name,
                'email': email,
                'phone': phone,
                'message': message
            }
            message = render_to_string('listings/contact_email.html', context)
            send_mail(subject, message, from_email, to_email, fail_silently=True)
            return redirect('listings:listing', listing_id=listing.id)
    else:
        form = ContactForm()
    return render(request, 'listings/contact.html', {'form': form})


def about(request):
    return render(request, 'listings/about.html')


def singleBlog(request):
    return render(request, 'listings/blog-single.html')


def predict(request):
    if request.method == 'POST':
        # get the input values from the form
        bathrooms = int(request.POST.get('bathrooms'))
        marla = float(request.POST.get('marla'))
        bedrooms = int(request.POST.get('bedrooms'))
        nearMasjid = int(request.POST.get('nearMasjid'))
        nearMarket = int(request.POST.get('nearMarket'))

        # load the model from the pickle file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(BASE_DIR, 'model_pickle'), 'rb') as f:
            model = pickle.load(f)

        # make the prediction using the loaded model
        prediction = model.predict([[bathrooms, marla, bedrooms, nearMasjid, nearMarket]])
        
        # round the predicted price to 2 decimal places
        predicted_price = round(prediction[0], 2)
        
        return render(request, 'prediction/predict_price.html', {'predicted_price': predicted_price})
    else:
        return render(request, 'prediction/predict_price.html')

