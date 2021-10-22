from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Site, OldLand, Domain, CodeExample, \
    TrafficSource, Country, CampaignStatus, Account, Cabinet, Company, Test


class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'name', 'site']
    list_display_links = ['name']
    search_fields = ['name']


class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'site_name',
                    'is_domain_link', 'domain_count', 'check_status',
                    ]
    list_display_links = ['site_name']




class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cab_link', 'daily', 'get_geo', 'get_sites', 'status' ]
    list_display_links = ['name', ]
    list_filter = ['status']
    # date_hierarchy = 'published'  # фильтр над списком модклий по дате

    autocomplete_fields = ['land']

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
    list_display = ['id', 'name', 'account', 'pixel', 'domain']
    list_display_links = ['name']
    autocomplete_fields = ['domain']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_ru', 'name_eng', 'short_name', 'phone_code']
    list_display_links = ['name_ru']


class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'source']
    list_display_links = ['name']


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
