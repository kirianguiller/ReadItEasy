from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home_book),
    path('books/', views.show_books_list),
    path('books/<language>/<id_book>/', views.show_chapter),
    path('books/<language>/<id_book>/<int:reader_chapter>', views.show_chapter),
    path('books/<language>/<id_book>/statistics/', views.show_statistics),
    # path('books/<language>/<id_book>/search/', views.show_search), # old POST pattern search
    path('books/<language>/<id_book>/search/<search>', views.show_search),
    # path('ajax_test/', views.ajax_test),
    path('send_ajax_json/', views.send_ajax_json),
    path('ajax_change_tokenization/', views.ajax_change_tokenization),
]