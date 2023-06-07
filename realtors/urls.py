from django.urls import path
from . import views


app_name = 'realtors'


urlpatterns = [
    # path('', views.realtors, name='realtors'),
    path('realtors/', views.realtors, name='realtors'),
    path('<int:realtor_id>/', views.realtor, name='realtor'),
    # path('realtor/<int:realtor_id>/', views.realtor, name='realtor'),
]
