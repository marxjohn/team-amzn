from Sift.models import Cluster
from django.contrib import admin

class ClusterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('ispinned', {'fields': ['ispinned'], 'classes': ['collapse']})
    ]
    # inlines = [ChoiceInline]
    list_display = ('name', 'ispinned')
    search_fields = ['name']

admin.site.register(Cluster, ClusterAdmin)