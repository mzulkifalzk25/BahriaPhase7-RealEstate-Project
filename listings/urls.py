from django.urls import path
from . import views


app_name = 'listings'


urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('predict/', views.predict, name='predict'),
    path('listings/', views.listings, name='listings'),
    path('<int:listing_id>/', views.listing, name='listing'),
    path('singleBlog/', views.singleBlog, name='singleBlog'),
    path('contact/', views.contact, name='contacts'),
    path('about/', views.about, name='about'),
]

