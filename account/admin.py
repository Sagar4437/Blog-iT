from django.contrib import admin
from .models import User
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['email','first_name','last_name','username','is_active']
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    ordering = ['-date_joined','username']

admin.site.register(User,UserAdmin)
