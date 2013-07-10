from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Account(models.Model):
	user = models.ForeignKey(User)
	#time = models.ManyToManyKey('TimeDetail')
	def __unicode__(self):
		return (self.user.username)

class TimeDetail(models.Model):
	user = models.ForeignKey('Account')
	weekday = models.CharField(max_length=10)
	time = models.TimeField()
	level = models.IntegerField()
	def __unicode__(self):
		return (self.user,time,weekday)