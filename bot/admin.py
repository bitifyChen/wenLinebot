from django.contrib import admin
from .models import *
class messageAdmin(admin.ModelAdmin):
    list_display = ('id','message_time', 'userID', 'groupID', 'message')
    list_filter = ('groupID',)

class line_userAdmin(admin.ModelAdmin):
    list_display = ('userID', 'username')

class codaAdmin(admin.ModelAdmin):
    list_display = ('end', 'groupID','lowest_num','height_num','answer_num')

admin.site.register(messagelog,messageAdmin)
admin.site.register(line_user,line_userAdmin)
admin.site.register(coda,codaAdmin)
