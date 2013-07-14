# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Account(models.Model):
	user = models.ForeignKey(User)
	hobby = models.CharField(max_length=100,blank=True)
	#time = models.ManyToManyKey('TimeDetail')
	def __unicode__(self):
		return (self.user.username)

class UserGroup(models.Model):
	group_name = models.CharField(max_length=50)
	user = models.ForeignKey('Account',related_name='group_own')
	member = models.ManyToManyField('Account',related_name='group_member')
	def __unicode__(self):
		return self.group_name

class TimeDetail(models.Model):
	user = models.ForeignKey('Account')
	weekday = models.CharField(max_length=10)
	star_time = models.TimeField()
	end_time = models.TimeField()
	level = models.IntegerField()
	def __unicode__(self):
		#return (self.user,u'%s'%self.time,self.weekday)
		return self.user.user.username+ ' ' +unicode(self.weekday)

class DateDetail(models.Model):
	user = models.ForeignKey('Account')
	star_date = models.DateField()
	end_date = models.DateField()
	level = models.IntegerField()