from django.urls import path
from . import views

urlpatterns = [
    path('dictionary/<language>/<user_word>/', views.show_word_data),
]