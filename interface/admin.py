from django.contrib import admin

# Register your models here.

from .models import  Task, Node, GlobalLimit,UserProfile, Banned

admin.site.register(Task)
admin.site.register(Node)
admin.site.register(GlobalLimit)
admin.site.register(UserProfile)
admin.site.register(Banned)