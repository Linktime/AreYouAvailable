# -*- coding:utf-8 -*-
from account.models import Account,UserGroup

class TimeData(object):
    count = None
    start_time = None
    end_time = None
    userlist = None

    def __init__(self,start_time,end_time,userlist,count=1):
        self.count = count
        self.start_time = start_time
        self.end_time = end_time
        self.userlist = userlist

    def add(self,user):
        self.count += 1
        self.userlist.append(user)

    def clone(self):
        td = TimeData(self.start_time,self.end_time,self.userlist[:],self.count)
        return td

    def __repr__(self):
        return '%s--%s %d'%(self.start_time,self.end_time,self.count)
    def __str__(self):
        return '%s-%s'%(self.start_time,self.end_time)
    def __eq__(self,obj):
        return self.start_time == obj.start_time and self.end_time == obj.end_time

def get_week_timeDetail_old(showmethod):
    #XXX
    #将timedetail重新按照星期分组,与下个方法相比，这个需要访问一次数据库，但是需要对list进行7次分组
    user_timedetail = showmethod.timedetail.all()
    user_weekday_1 = filter(lambda x:x.weekday==u'1',user_timedetail)
    user_weekday_2 = filter(lambda x:x.weekday==u'2',user_timedetail)
    user_weekday_3 = filter(lambda x:x.weekday==u'3',user_timedetail)
    user_weekday_4 = filter(lambda x:x.weekday==u'4',user_timedetail)
    user_weekday_5 = filter(lambda x:x.weekday==u'5',user_timedetail)
    user_weekday_6 = filter(lambda x:x.weekday==u'6',user_timedetail)
    user_weekday_7 = filter(lambda x:x.weekday==u'7',user_timedetail)
    user_weekday = [user_weekday_1,user_weekday_2,user_weekday_3,user_weekday_4,user_weekday_5,user_weekday_6,user_weekday_7]
    return user_weekday

def get_week_timeDetail(showmethod):
    #与上个方法相比，这个需要访问7次数据库
    user_weekday_1 = showmethod.timedetail.filter(weekday=u'1')
    user_weekday_2 = showmethod.timedetail.filter(weekday=u'2')
    user_weekday_3 = showmethod.timedetail.filter(weekday=u'3')
    user_weekday_4 = showmethod.timedetail.filter(weekday=u'4')
    user_weekday_5 = showmethod.timedetail.filter(weekday=u'5')
    user_weekday_6 = showmethod.timedetail.filter(weekday=u'6')
    user_weekday_7 = showmethod.timedetail.filter(weekday=u'7')
    user_weekday = [user_weekday_1,user_weekday_2,user_weekday_3,user_weekday_4,user_weekday_5,user_weekday_6,user_weekday_7]
    return user_weekday

# new method

def get_oneDay_freeTime_data(all_oneDays,user_oneDays,user):
    # Sort by Great > Bellow
    all_oneDays = sorted(all_oneDays,cmp=lambda u_x,u_y:cmp(u_y.start_time,u_x.start_time))
    user_oneDays = sorted(user_oneDays,cmp=lambda u_x,u_y:cmp(u_y.start_time,u_x.start_time))

    new_all_oneDays = all_oneDays[:]

    while all_oneDays or user_oneDays:
        if all_oneDays:
            all_oneDay=all_oneDays.pop()
        else:
            all_oneDay = None
        if user_oneDays:
            user_oneDay=user_oneDays.pop()
        else:
            user_oneDay = None

        if all_oneDay and not user_oneDay:
            pass
        elif user_oneDay and not all_oneDay:
            td = TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,])
            new_all_oneDays.append(td)
        else:
            if all_oneDay.start_time == user_oneDay.start_time:
                if all_oneDay.end_time == user_oneDay.end_time:
                    index = new_all_oneDays.index(all_oneDay)
                    new_all_oneDays[index].add(user)
                elif all_oneDay.end_time < user_oneDay.end_time:
                    tdmid = all_oneDay.clone()
                    index = new_all_oneDays.index(tdmid)
                    tdmid.add(user)
                    new_all_oneDays[index] = tdmid
                else :
                    tdmid = all_oneDay.clone()
                    tdmid.end_time = user_oneDay.end_time
                    tdmid.add(user)
                    new_all_oneDays.append(tdmid)
            elif all_oneDay.start_time < user_oneDay.start_time:
                if all_oneDay.end_time <= user_oneDay.start_time:
                    user_oneDays.append(user_oneDay)
                elif all_oneDay.end_time > user_oneDay.start_time:
                    if all_oneDay.end_time < user_oneDay.end_time:
                        tdmid = all_oneDay.clone()
                        tdmid.add(user)
                        tdmid.start_time = user_oneDay.start_time
                        new_all_oneDays.append(tdmid)
                        tdnext = TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,])
                        new_all_oneDays.append(tdnext)
                    else:
                        tdmid = all_oneDay.clone()
                        tdmid.start_time = user_oneDay.start_time
                        tdmid.end_time=user_oneDay.end_time
                        tdmid.add(user)
                        new_all_oneDays.append(tdmid)
            else :
                if user_oneDay.end_time <= all_oneDay.start_time:
                    new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
                    all_oneDays.append(all_oneDay)
                else :
                    if user_oneDay.end_time < all_oneDay.end_time:
                        new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
                        tdmid = all_oneDay.clone()
                        tdmid.end_time=user_oneDay.end_time
                        new_all_oneDays.append(tdmid)

                    else :
                        tdmid = all_oneDay.clone()
                        index = new_all_oneDays.index(tdmid)
                        tdmid.add(user)
                        new_all_oneDays[index] = tdmid
                        new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
    return new_all_oneDays

def get_oneWeek_freeTime_Data(all_oneWeeks,user_oneWeeks,user):
    new_all_oneWeeks = []
    for index in range(7):
        new_all_oneWeeks.append(get_oneDay_freeTime_data(all_oneWeeks[index],user_oneWeeks[index],user))

    #FIXME
    # for (all_oneDays,user_oneDays) in (all_oneWeeks,user_oneWeeks):
    #     new_all_oneWeeks.append(get_oneDay_freeTime_data(all_oneDays,user_oneDays,user))

    return new_all_oneWeeks

def get_Somebody_freeTime_Data(user,user_showmethod,memberlist):
    user = Account.objects.get(user=user)    
    try :
        user_timedetail = user_showmethod.timedetail
        user_weekdays = get_week_timeDetail(user_showmethod)
        weekday_data= [[],[],[],[],[],[],[]]
        user_weekday_data = get_oneWeek_freeTime_Data(weekday_data,user_weekdays,user)
        
        new_weekday_data = user_weekday_data
        for member in memberlist:
            member_showmethod = member_group.showmethod
            member_weekdays = get_week_timeDetail(member_showmethod)
            new_weekday_data = get_oneWeek_freeTime_Data(new_weekday_data,member_weekdays,member)
        return new_weekday_data
    except Account.DoesNotExist:
        pass


def get_userGroup_freeTime_Data(user,group_name):
    #user = Account.objects.get(user=user)    
    try :
        user_group = UserGroup.objects.get(user=user,group_name=group_name)
        user_showmethod = user_group.showmethod
        user_timedetail = user_showmethod.timedetail
        user_weekdays = get_week_timeDetail(user_showmethod)
        weekday_data= [[],[],[],[],[],[],[]]
        user_weekday_data = get_oneWeek_freeTime_Data(weekday_data,user_weekdays,user)
        
        new_weekday_data = user_weekday_data
        for member in user_group.member.all():
            member_group = user.usergroup_member.get(user=member)
            member_showmethod = member_group.showmethod
            member_weekdays = get_week_timeDetail(member_showmethod)
            new_weekday_data = get_oneWeek_freeTime_Data(new_weekday_data,member_weekdays,member)
        return new_weekday_data
    except Account.DoesNotExist:
        pass
