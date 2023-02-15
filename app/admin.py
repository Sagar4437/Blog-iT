from django.contrib import admin
from . models import Blog,Category
# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','short_description','views','likes','created_at','updated_at']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Blog,BlogAdmin)
admin.site.register(Category,CategoryAdmin)
