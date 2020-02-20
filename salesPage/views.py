from django.shortcuts import render


# Create your views here.


def cover_sales(req):
    return render(req, 'cover/cover_sales.html')
