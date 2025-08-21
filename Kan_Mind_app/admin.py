from django.contrib import admin
from .models import Board, BoardUser, Task
# Register your models here.



class AdminTask(admin.ModelAdmin):
    list_display=["description", "title","status"]

class AdminBoard(admin.ModelAdmin):
    list_display=["title", "owner"]

class BoardUserAdmin(admin.ModelAdmin):
    list_display=["user","board","role"]


admin.site.register(Board)
admin.site.register(BoardUser)
admin.site.register(Task, AdminTask)