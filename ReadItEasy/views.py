from django.shortcuts import render


def show_home(request):
    return render(request, "ReadItEasy/home.html")


def show_contact(request):
    return render(request, "ReadItEasy/contact.html")