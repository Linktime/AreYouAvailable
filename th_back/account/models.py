# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Account(models.Model):
	user = models.OneToOneField(User)
	hobby = models.CharField(max_length=100,blank=True)
	#time = models.ManyToManyKey('TimeDetail')
	def __unicode__(self):
		return (self.user.username)

class UserGroup(models.Model):
	group_name = models.CharField(max_length=50)
	user = models.ForeignKey('Account',related_name='usergroup_user')
	member = models.ManyToManyField('Account',related_name='usergroup_member')
	showmethod = models.ForeignKey('ShowMethod',related_name='usergroup_showmethod')
	def __unicode__(self):
		return self.user.user.username + ' ' + self.group_name

class TimeDetail(models.Model):
	user = models.ForeignKey('Account',related_name='timedetail_user')
	weekday = models.CharField(max_length=10,choices=(('1','星期一'),
														('2','星期二'),
														('3','星期三'),
														('4','星期四'),
														('5','星期五'),
														('6','星期六'),
														('7','星期日')))
	start_time = models.TimeField()
	end_time = models.TimeField()
	level = models.IntegerField(default=3)
	free = models.BooleanField(default=False)
	def __unicode__(self):
		#return (self.user,u'%s'%self.time,self.weekday)
		return self.user.user.username+ ' ' +unicode(self.weekday) + ' ' + unicode(self.start_time) + '-' + unicode(self.end_time)

class DateDetail(models.Model):
	user = models.ForeignKey('Account',related_name='datedetail_user')
	start_date = models.DateField()
	end_date = models.DateField()
	level = models.IntegerField(default=3)
	def __unicode__(self):
		return self.user.user.username + unicode(self.start_date) + '-' + unicode(self.end_date)

class ShowMethod(models.Model):
	user = models.ForeignKey('Account',related_name='showmethod_user')
	timedetail = models.ManyToManyField('TimeDetail',blank=True,related_name='showmethod_timedetail')
	datedetail = models.ManyToManyField('DateDetail',blank=True,related_name='showmethod_datedetail')
	def __unicode__(self):
		return self.user.user.username