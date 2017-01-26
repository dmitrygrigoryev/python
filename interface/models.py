from __future__ import unicode_literals
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user_id = models.OneToOneField(User)
    score = models.IntegerField(default=100)
    launch_score = models.IntegerField(default=0)
    def __str__(self):
        return ':'.join((self.user_id.username,str(self.score)))
        
class Banned(models.Model):
    user_id = models.OneToOneField(User,unique=True,primary_key=True)
    two_days = datetime.timedelta(days=2)
    banned_from = models.DateTimeField('date banned',default=timezone.now())
    banned_to = models.DateTimeField('date unbanned',default=timezone.now()+two_days)

    
class Node(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    node_ip = models.CharField(max_length=20)
    node_cpu = models.IntegerField(default=1)
    node_ram = models.IntegerField(default=0)
    in_work = models.BooleanField(default=False)
    online = models.BooleanField(default=False)
    def __str__(self):
        return ':'.join((self.user_id.username,self.node_ip))
        
class Task(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    options = models.TextField(max_length=255,default='{}')
    cpu = models.IntegerField(default=1)
    ram = models.IntegerField(default=0)
    status = models.CharField(max_length=30,default='in queue')
    date = models.DateTimeField('published date',default=timezone.now())
    prime = models.BooleanField(default=False)
    moretime = models.BooleanField(default=False)
    defnode = models.BooleanField(default=False)
    node_id = models.IntegerField(default=-1)
    # def __str__(self):
        # return ':'.join((self.path,str(self.user_id)))

class GlobalLimit(models.Model):
    max_launch = models.IntegerField(default=5)
    task_max_time = models.IntegerField(default=240)
    def __str__(self):
        return "max launch: %s; task_max_time: %s"%(str(self.max_launch),str(self.task_max_time))