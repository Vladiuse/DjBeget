from django.urls import path
from . import views

app_name = 'office'
urlpatterns = [
    path('', views.sites, name='sites'),
    path('add/<str:summ>/', views.add_spend, name='add_spend'),
    path('update_sites/', views.update_sites, name='update_sites'),
    path('get-title/<int:hard>/', views.get_site_title, name='get_site_title'),
    path('old-lands', views.old_lands, name='old_lands'),
    path('requisites', views.requisites, name='requisites'),
    path('checker/<int:site_id>/', views.checker, name='checker'),
    path('domains', views.domains, name='domains'),
    path('domains/<int:dom_id>/<str:source>/<str:new_status>/', views.domain_change_status, name='change_status'),
    path('learn-code/', views.learn_code, name='learn_code'),
    ]