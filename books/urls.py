from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_user_text),
    path('books/collection', views.collection),
    path('books/<id_book>', views.print_book),
]