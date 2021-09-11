from django.contrib import admin
from .models import Site, OldLand, Domain, CodeExample
# Register your models here.

# class StreamAdmin(admin.ModelAdmin):
#     list_display = ['id', 'baer', 'spend', 'description']

admin.site.register(Site)
admin.site.register(OldLand)
admin.site.register(Domain)
admin.site.register(CodeExample)
