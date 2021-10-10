from django.contrib import admin

from .models import Site, OldLand, Domain, CodeExample, \
    TrafficSource, Country, CampaignStatus, Account, Cabinet, Company, Test


class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'name', 'site']
    search_fields = ['name']


class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'site_name',
                    'is_domain_link', 'domain_count', 'check_status',
                    ]


class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cab', 'get_account', 'get_geo', 'get_sites', 'status']

    # autocomplete_fields = ['land']

    def get_account(self, obj):
        return obj.cab.account

    def get_geo(self, obj):
        return [geo.short_name for geo in obj.geo.all()]

    def get_sites(self, obj):
        return [land.name for land in obj.land.all()]


class CabinetAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'pixel', 'domain']
    autocomplete_fields = ['domain']


class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name_ru', 'name_eng', 'short_name', 'phone_code']


admin.site.register(Test)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Account)
admin.site.register(Cabinet, CabinetAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(OldLand)
admin.site.register(Domain, DomainAdmin)
admin.site.register(CodeExample)
admin.site.register(TrafficSource)
admin.site.register(CampaignStatus)
admin.site.register(Country, CountryAdmin)
