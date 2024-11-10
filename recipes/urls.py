from django.contrib import admin
from django.urls import path, include

from recipes.views import get_recipes

urlpatterns = [
    path('get/', get_recipes, name='get_recipes'),
]
