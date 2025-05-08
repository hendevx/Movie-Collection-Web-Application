from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Welcome to the Movie Collection API!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Add this line for the root URL
    path('', include('movie_collection.urls')),
]