from django.contrib import admin

from .models import Site, OldLand, Domain, CodeExample, \
    TrafficSource, Country, CampaignStatus, Account, Cabinet


# Register your models here.


class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'name', 'site']


class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'site_name',
                    'is_domain_link', 'domain_count',
                    ]


admin.site.register(Account)
admin.site.register(Cabinet)
admin.site.register(Site, SiteAdmin)
admin.site.register(OldLand)
admin.site.register(Domain, DomainAdmin)
admin.site.register(CodeExample)
admin.site.register(TrafficSource)
admin.site.register(CampaignStatus)
admin.site.register(Country)
