from django.urls import path
from . import views

app_name = 'office'
urlpatterns = [
    path('', views.sites, name='sites'),
    path('update_sites/', views.update_sites, name='update_sites'),
    path('get-title/<int:hard>/', views.get_site_title, name='get_site_title'),
    path('old-lands', views.old_lands, name='old_lands'),
    path('requisites', views.requisites, name='requisites'),
    # path('checker/<int:site_id>/<str:mode>/', views.checker, name='checker'),
    path('checker/<int:site_id>/<int:mode>/', views.checker, name='checker'),
    path('domains', views.domains, name='domains'),
    path('domains/<int:dom_id>/<str:source>/<str:new_status>/', views.domain_change_status, name='change_status'),
    path('campanings/', views.campanings, name='campanings'),
    path('delete_site/<int:site_id>/', views.delete_site, name='del_site'),
    path('api/', views.domains_list_api),
    path('api/campanings/', views.company_list_api),
    path('api/campaning_detail/<int:pk>/', views.campaning_detail),
    path('api/change_domain_desc/<int:pk>/', views.domains_detail),
    path('api/zapusk/', views.zapusk_data),
    path('api/create_capmaning/', views.create_capmaning),
    path('api/add_lead/', views.add_lead),
    path('leads/', views.all_leads, name='leads'),
    path('main/', views.main, name='main'),
    path('update_leads/', views.update_leads, name='update_leads'),
    ]