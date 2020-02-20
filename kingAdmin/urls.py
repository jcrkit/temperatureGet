from django.urls import path, re_path
from kingAdmin import views

urlpatterns = [
    path('', views.king_table, name='king_table'),
    re_path('^(\w+)/(\w+)/$', views.king_index, name='king_index'),
    re_path('^(\w+)/(\w+)/(\d+)/change/$', views.king_change, name='king_change'),
    re_path('^(\w+)/(\w+)/(\d+)/change/password/reset/$', views.password_reset, name='king_reset'),
    re_path('^(\w+)/(\w+)/(\d+)/delete/$', views.king_delete, name='king_delete'),
    re_path('^(\w+)/(\w+)/add/$', views.king_add, name='king_add'),
]
