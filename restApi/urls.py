from django.urls import path
from restApi import views

urlpatterns = [
    path('words/', views.word_list),
    path('words/<r_word>/', views.word_detail),
]