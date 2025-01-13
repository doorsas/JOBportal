from django.urls import path
from . import views

urlpatterns = [
    # Pvz., pagrindinis EOR puslapis
    path('', views.eor_dashboard, name='eor_dashboard'),
]