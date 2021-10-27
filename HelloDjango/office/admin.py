from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Site, OldLand, Domain, CodeExample, \
    TrafficSource, Country, CampaignStatus, Account, Cabinet, Company, Test, Lead, Employee


class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'name', 'site']
    list_display_links = ['name']
    search_fields = ['name']


class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'site_name',
                    'is_domain_link', 'domain_count', 'check_status', 'employee',
                    ]
    list_display_links = ['site_name']




class CompanyAdmin(admin.ModelAdmin):
    list_display = ['traff_source', 'name', 'cab_link', 'daily', 'get_geo', 'get_sites', 'status' ]
    list_display_links = ['name', ]
    list_filter = ['status',]
    # date_hierarchy = 'published'  # фильтр над списком моделей по дате

    autocomplete_fields = ['land']

    def traff_source(self,obj):
        if obj.cab:
            return obj.cab.account.source.name

    def cab_link(self, obj):
        """Получить ссылку на обьект"""
        if obj.cab:
            link = reverse("admin:office_cabinet_change", args=[obj.cab.id])
            return format_html(f'<a href="{link}">{obj.cab.name}</a>')
    cab_link.short_description = 'Кабинет'

    # self.go_to_author.allow_tags = True
    # def get_account(self, obj):
    #     return obj.cab.account

    def get_geo(self, obj):
        return [geo.short_name for geo in obj.geo.all()]

    get_geo.short_description = 'Гео'

    def get_sites(self, obj):
        return [land.name for land in obj.land.all()]

    get_sites.short_description = 'Домены'


class CabinetAdmin(admin.ModelAdmin):
    list_display = ['get_source', 'account','name', 'pixel', 'domain', ]
    list_display_links = ['name']
    autocomplete_fields = ['domain', 'account']

    list_filter = ['account']

    def get_source(self, obj):
        return obj.account.source.name


class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_ru', 'name_eng', 'short_name', 'phone_code']
    list_display_links = ['name_ru']


class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'source']
    list_display_links = ['name']
    search_fields = ['name']

class LeadAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Lead._meta.get_fields()]


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'code']

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Test)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Cabinet, CabinetAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(OldLand)
admin.site.register(Domain, DomainAdmin)
admin.site.register(CodeExample)
admin.site.register(TrafficSource)
admin.site.register(CampaignStatus)
admin.site.register(Country, CountryAdmin)
admin.site.register(Lead, LeadAdmin)
