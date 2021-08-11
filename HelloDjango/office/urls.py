from django.urls import path
from . import views

app_name = 'office'
urlpatterns = [
    path('', views.index, name='index'),
    path('add/<str:summ>/', views.add_spend, name='add_spend'),
    path('update-domains', views.update_domains, name='update_domains'),
    path('get-title', views.get_title, name='get_title'),
    path('old-lands', views.old_lands, name='old_lands'),
    path('requisites', views.requisites, name='requisites'),
    path('checker/<int:site_id>/', views.checker, name='checker'),
    ]