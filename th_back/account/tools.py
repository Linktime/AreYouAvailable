# -*- coding:utf-8 -*-
from account.models import Account,UserGroup

def get_time_user(user,group_name):
    #source_data = request.GET
    #user = request.user
    user = Account.objects.get(user=user)
    #group_name = source_data['group']
    try :
        user_group = UserGroup.objects.get(user=user,group_name=group_name)
        user_showmethod = user_group.showmethod
        user_timedetail = user_showmethod.timedetail.all()
        weekday_times = [{},{},{},{},{},{},{}]
        #print user_timedetail
        user_weekdays = get_week(user_timedetail)
        '''
        for (user_weekday,weekday_time) in (user_weekdays,weekday_times):
            weekday_time = get_oneday_time(weekday_time,user_weekday,user)
        
        #print weekday_times
        
        for member in user_group.member.all():
            member_group = user.usergroup_member.get(user=member)
            member_showmethod = member_group.showmethod
            member_timedetail = member_showmethod.timedetail.all()
            member_weekdays = get_weekday(member_timedetail)
            for (member_weekday,weekday_time) in (member_weekdays,weekday_times):
                weekday_time = get_oneday_time(weekday_time,member_weekday,member)
        '''
        #print weekday_times
        user_weekday_1 = user_weekdays[0]
        print get_oneday_time({},user_weekday_1,user)

    except UserGroup.DoesNotExist:
        user_group = None


def get_week(user_timedetail):
    user_weekday_1 = filter(lambda x:x.weekday==u'1',user_timedetail)
    user_weekday_2 = filter(lambda x:x.weekday==u'2',user_timedetail)
    user_weekday_3 = filter(lambda x:x.weekday==u'3',user_timedetail)
    user_weekday_4 = filter(lambda x:x.weekday==u'4',user_timedetail)
    user_weekday_5 = filter(lambda x:x.weekday==u'5',user_timedetail)
    user_weekday_6 = filter(lambda x:x.weekday==u'6',user_timedetail)
    user_weekday_7 = filter(lambda x:x.weekday==u'7',user_timedetail)
    user_weekday = [user_weekday_1,user_weekday_2,user_weekday_3,user_weekday_4,user_weekday_5,user_weekday_6,user_weekday_7]
    return user_week

# Old method
'''
def get_oneday_time(oneday_times,user_times,user):
    for user_time in user_times:
        oneday_time_start = oneday_times.get('%s'%user_time.start_time)
        if not oneday_time_start:
            oneday_times['%s'%user_time.start_time] = {'%s'%user_time.end_time:{'count':1,'user':[user,]}}
        else :
            oneday_time_end = oneday_time_start.get('%s'%user_time.end_time)
            if oneday_time_end:
                oneday_time_end['count'] += 1
                oneday_time_end['user'].append(user)
            else :
                oneday_time_start['%s'%user_time_end] = {'count':1,'user':[user,]}
    return oneday_times
'''

# new method

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
        td = TimeData(self.start_time,self.end_time,self.userlist,self.count)
        return td

    def __repr__(self):
        return '%s--%s %d'%(self.start_time,self.end_time,self.count)
    def __str__(self):
        return '%s--%s'%(self.start_time,self.end_time)
    def __eq__(self,obj):
        return self.start_time == obj.start_time and self.end_time == obj.end_time

def get_oneDay_data(all_oneDays,user_oneDays,user):
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
            if all_oneDay.start_time == user_oneDay.start_time and all_oneDay.end_time == user_oneDay.end_time:
                index = new_all_oneDays.index(all_oneDay)
                new_all_oneDays[index].add(user)
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
                        tdmin.end_time=user_oneDay.end_time
                        new_all_oneDays.append(tdmid)

                    else :
                        tdmid = all_oneDay.clone()
                        index = new_all_oneDays.index(tdmid)
                        tdmid.add(user)
                        new_all_oneDays[index] = tdmid
                        new_all_oneDays.append(TimeData(user_oneDay.start_time,user_oneDay.end_time,[user,]))
    return new_all_oneDays

def get_oneWeek_Data():
    #TODO
    pass