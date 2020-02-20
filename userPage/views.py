from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tempAPP import models

# Create your views here.


def cover_user(req):
    return render(req, 'cover/cover_user.html')


@login_required
def user_page(req):
    tempData = models.Temperature.objects.filter(userId=req.user.id)
    tempName = models.Temperature._meta.verbose_name
    if req.method == 'POST':
        selected_ids = req.POST.get('selected_ids')
        if selected_ids:
            selected_ids = selected_ids.split(',')
            print(selected_ids)
            models.Temperature.objects.filter(id__in=selected_ids).delete()
    return render(req, 'userPage/mainPage.html', {'req': req,
                                                  'tempData': tempData,
                                                  'tempName': tempName})
