from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_book),
    path('books/', views.show_languages),
    path('books/<language>/', views.show_books),
    # path('books/<id_book>/', views.show_chinese_book),
    path('books/<language>/<id_book>/', views.show_chapter),
    path('books/<language>/<id_book>/<int:reader_chapter>', views.show_chapter),
]