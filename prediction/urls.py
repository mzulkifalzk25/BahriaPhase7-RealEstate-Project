from django.urls import path
from . import views


urlpatterns = [
    path('predict_price/', views.predict_price, name="predict_price"),
    path('price_map/', views.price_map, name="price_map"),
    path('report/', views.report, name="report"),
]