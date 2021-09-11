from django.contrib import admin

from .models import Site, OldLand, Domain, CodeExample, PublishedSite


# Register your models here.

class PublishedSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'site_dir', 'domain']


class DomainAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'name', 'site']


class SiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'beget_id', 'site_name', 'is_domain_link', 'domain_count', ]


admin.site.register(PublishedSite, PublishedSiteAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(OldLand)
admin.site.register(Domain, DomainAdmin)
admin.site.register(CodeExample)
