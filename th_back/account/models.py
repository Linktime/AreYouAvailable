# -*- coding:utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import Signal
from django.db.models.signals import post_save

accepted_signal = Signal(providing_args=['activity','member'])

# Create your models here.

class Account(models.Model):
    user = models.OneToOneField(User)
    hobby = models.CharField(max_length=200,blank=True)
    #time = models.ManyToManyKey('TimeDetail')
    def __unicode__(self):
        return (self.user.username)

class UserGroup(models.Model):
    group_name = models.CharField(max_length=50)
    user = models.ForeignKey(User,related_name='usergroup_user')
    member = models.ManyToManyField(User,related_name='usergroup_member')
    #showmethod = models.ForeignKey('ShowMethod',related_name='usergroup_showmethod')
    def __unicode__(self):
        return self.user.username + ' ' + self.group_name

class TimeDetail(models.Model):
    user = models.ForeignKey(User,related_name='timedetail_user')
    weekday = models.CharField(max_length=10,choices=(('1','星期一'),
                                                        ('2','星期二'),
                                                        ('3','星期三'),
                                                        ('4','星期四'),
                                                        ('5','星期五'),
                                                        ('6','星期六'),
                                                        ('7','星期日')))
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=50,null=True,blank=True)
    useto = models.ManyToManyField(User,related_name='timedetail_userto',null=True,blank=True)
    useto_group = models.ManyToManyField(UserGroup,related_name='timedetail_userto_group',null=True,blank=True)
    level = models.IntegerField(default=3)
    free = models.BooleanField(default=False)
    def __unicode__(self):
        #return (self.user,u'%s'%self.time,self.weekday)
        return self.user.username+ ' ' +unicode(self.weekday) + ' ' + unicode(self.start_time) + '-' + unicode(self.end_time)

    # def add_group(self,group):
    #     self.useto_group.add(group)
    #     members = group.member.all()
    #     for member in members:
    #         #usetos = self.useto.all()
    #         #if member not in usetos:
    #         self.useto.add(member)
    #     self.save()

    # def remove_group(self,group):
    #     members = group.member.all()
    #     try :
    #         for member in members:
    #             self.userto.remove(member)
    #     except :
    #         pass
    #     self.useto_group.remove(group)
    #     self.save()



class DateDetail(models.Model):
    user = models.ForeignKey(User,related_name='datedetail_user')
    start_date = models.DateField()
    end_date = models.DateField()
    level = models.IntegerField(default=3)
    def __unicode__(self):
        return self.user.username + unicode(self.start_date) + '-' + unicode(self.end_date)

# class ShowMethod(models.Model):
#     user = models.ForeignKey(User,related_name='showmethod_user')
#     showmethod_name = models.CharField(max_length=50)
#     using_begin = models.DateField(default=settings.TODAY,blank=True)
#     using_end = models.DateField(default=settings.LAST_DAY,blank=True)
#     timedetail = models.ManyToManyField('TimeDetail',blank=True,related_name='showmethod_timedetail')
#     datedetail = models.ManyToManyField('DateDetail',blank=True,related_name='showmethod_datedetail')
#     def __unicode__(self):
#         return self.user.username

class ActivityTime(models.Model):
    user = models.ForeignKey(User,related_name="activitytime_user")
    activity = models.ForeignKey('Activity')
    start_date = models.DateField(blank=True,null=True)
    end_date = models.DateField(blank=True,null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __unicode__(self):
        return self.activity.name + ' ' + unicode(self.start_time) + '--' + unicode(self.end_time)

class Activity(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User,related_name="activity_user")
    participant = models.ManyToManyField(User,related_name="activity_participant",blank=True,null=True)
    time = models.ManyToManyField(ActivityTime,related_name="activity_time",null=True,blank=True)
    place = models.CharField(max_length=100,blank=True,null=True)
    description = models.CharField(max_length=200,blank=True,null=True)

    def __unicode__(self):
        return self.name

class NotifyBase(models.Model):
    sender = models.ForeignKey(User,related_name="notify_sender")
    member = models.ForeignKey(User,related_name="notify_member")
    time = models.DateTimeField(auto_now=True)
    readed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    def __unicode__(self):
        return u'%s to %s'%(self.sender.username,self.member.username)

class ActivityNotify(NotifyBase):
    activity = models.ForeignKey(Activity,related_name="activitynotify_activity")
    def save(self):
        if self.accepted == True :
            accepted_signal.send(sender=self.__class__,activity=self.activity,member=self.member)
        super(ActivityNotify,self).save()


def accepted_activity(activity,member,**kwargs):
    activity.participant.add(member)
    activity.save()

def create_default_group(sender,**kwargs):
    if kwargs['created'] == True:
        group = UserGroup()
        user = kwargs['instance']
        group.user = user
        group.group_name = u"默认分组"
        group.save()

post_save.connect(create_default_group,sender=User)
accepted_signal.connect(accepted_activity,sender=ActivityNotify)