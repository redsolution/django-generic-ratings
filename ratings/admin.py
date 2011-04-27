from django.contrib import admin

from ratings import models

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'key', 'average', 'total', 'num_votes')
    list_filter = ['content_type']
    ordering = ('average', 'num_votes')
    
admin.site.register(models.Score, ScoreAdmin)
