from django.contrib import admin
from .models import Stream, Site, OldLand, Domain
# Register your models here.

class StreamAdmin(admin.ModelAdmin):
    list_display = ['id', 'baer', 'spend', 'description']

admin.site.register(Stream, StreamAdmin)
admin.site.register(Site)
admin.site.register(OldLand)
admin.site.register(Domain)
