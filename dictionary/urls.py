from django.urls import path
from . import views

urlpatterns = [
    path('dictionary/<language>/words/', views.view_words_list),
    path('dictionary/<language>/<user_word>/', views.view_word_data),
    path('dictionary/ajax_interact_known_word/', views.ajax_interact_known_word),
]