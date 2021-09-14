from django.db import models

class messagelog(models.Model):
    groupID = models.CharField(max_length=50, default='')
    userID = models.CharField(max_length=50, default='')
    message = models.CharField(max_length=255, blank=True, default='')
    message_time = models.DateTimeField(auto_now_add=True)

class line_user(models.Model):
    userID = models.CharField(max_length=50, default='')
    username = models.CharField(max_length=50, default='')

class coda(models.Model):
    creat_time = models.DateTimeField(auto_now_add=True)
    goal_time = models.DateTimeField(auto_now_add=True)
    groupID = models.CharField(max_length=50, default='')
    end = models.BooleanField(default=False)
    lowest_num = models.DecimalField(max_digits=3,decimal_places=0,null=True)
    answer_num = models.DecimalField(max_digits=3,decimal_places=0,null=True)
    height_num = models.DecimalField(max_digits=3,decimal_places=0,null=True)
