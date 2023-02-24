from django.contrib import admin
from . models import Blog,Category,Newsletter

from taggit.models import Tag, TaggedItem
# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','short_description','views','likes','created_at','updated_at']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email','is_active','created_at']

admin.site.register(Blog,BlogAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Newsletter,NewsletterAdmin)
