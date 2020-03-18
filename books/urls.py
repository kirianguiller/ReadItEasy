from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home_book),
    path('books/', views.show_books_list),
    path('books/<language>/<id_book>/', views.show_chapter),
    path('books/<language>/<id_book>/<int:reader_chapter>', views.show_chapter),
    path('books/<language>/<id_book>/words/', views.show_book_words),
    path('books/<language>/<id_book>/search/<search>', views.show_search),
    path('ajax_word_data/', views.ajax_word_data),
    path('ajax_change_tokenization/', views.ajax_change_tokenization),
    path('api/<id_book>/<int:reader_chapter>', views.API_mandarin_chapter),


]