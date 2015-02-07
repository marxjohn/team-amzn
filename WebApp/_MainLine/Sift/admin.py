from Sift.models import Cluster
from django.contrib import admin

class ClusterAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name']}),
        ('pinned', {'fields': ['pinned'], 'classes': ['collapse']})
    ]
    # inlines = [ChoiceInline]
    list_display = ('name', 'pinned')
    search_fields = ['name']

admin.site.register(Cluster, ClusterAdmin)