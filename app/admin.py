from django.contrib import admin
from . models import Blog,Category,Newsletter,Subscription

# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','short_description','views','likes','created_at','updated_at']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email','is_active','created_at']

class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['creator','all_subscribers','total']

    def all_subscribers(self, creatorObj):
        return ", ".join([p.username for p in creatorObj.subscribers.all()])

    def total(self, creatorObj):
        return creatorObj.subscribers.count()

admin.site.register(Blog,BlogAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Newsletter,NewsletterAdmin)
admin.site.register(Subscription,SubscriptionsAdmin)
