from django.contrib import admin

from .models import Site, OldLand, Domain, CodeExample, \
    TrafficSource, Country, CampaignStatus, Account, Cabinet, Company


# Register your models here.


class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'name', 'site']


class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'site_name',
                    'is_domain_link', 'domain_count',
                    ]

class CompanyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'cab', 'get_account', 'get_geo', 'get_sites', 'status']

    def get_account(self, obj):
        return obj.cab.account

    def get_geo(self, obj):
        return [geo.short_name for geo in obj.geo.all()]

    def get_sites(self, obj):
        return [land.name for land in obj.land.all()]

class CabinetAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'domain']

admin.site.register(Company, CompanyAdmin)
admin.site.register(Account)
admin.site.register(Cabinet, CabinetAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(OldLand)
admin.site.register(Domain, DomainAdmin)
admin.site.register(CodeExample)
admin.site.register(TrafficSource)
admin.site.register(CampaignStatus)
admin.site.register(Country)
