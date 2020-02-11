from django.urls import path
from . import views

urlpatterns = [
    path('dictionary/<language>/<user_word>/', views.show_word_data),
    path('dictionary/getAJAX_user_known_word/', views.getAJAX_user_known_word),
    path('dictionary/getAJAX_add_known_word/', views.getAJAX_add_known_word),

]